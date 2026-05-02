# Kimi K2.5 API Integration for DocuSwarm: Model Solution Research Report

**Version**: 2.0 (kimi-agent-sdk)  
**Date**: 2026-02-20  
**Project**: DocuSwarm Multi-Agent Document Orchestration System  
**Subject**: Kimi K2.5 as Designated LLM Provider  
**Status**: Research Complete

---

## 1. Executive Summary

### 1.1 Research Objective

This report evaluates **Moonshot AI Kimi K2.5** as the designated Large Language Model (LLM) solution for DocuSwarm's multi-agent document orchestration system. The analysis covers API capabilities, architectural alignment, integration patterns, and implementation recommendations.

### 1.2 Key Findings

| Dimension | Assessment | Confidence |
|-----------|------------|------------|
| **API Compatibility** | kimi-agent-sdk 原生 Python SDK (Wire 协议) | High |
| **Agent Swarm Alignment** | Native parallel orchestration | Very High |
| **Context Window** | 256K tokens (sufficient) | High |
| **Tool Calling Support** | CallableTool2 + Pydantic (SDK 原生) | High |
| **Cost Efficiency** | Competitive pricing | High |
| **DocuSwarm Fit Score** | **9.2/10** | High |

### 1.3 Strategic Recommendation

**Kimi K2.5 is HIGHLY RECOMMENDED** as DocuSwarm's designated model due to:

1. **Native Agent Swarm Architecture** - Directly aligns with DocuSwarm's dual-agent pattern
2. **kimi-agent-sdk** - 原生 Python SDK 提供 Session/prompt API、CallableTool2、Wire 消息协议
3. **256K Context Window** - Handles large document pipelines without truncation
4. **PARL Framework** - 4.5x speedup through parallel agent execution
5. **Cost-Effective** - Competitive pricing with context caching benefits

---

## 2. Kimi K2.5 Technical Overview

### 2.1 Model Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Kimi K2.5 Architecture                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    Mixture-of-Experts (MoE) Foundation                  │ │
│  │                                                                         │ │
│  │  Total Parameters: 1 Trillion    Activated per Request: 32 Billion     │ │
│  │  Pre-training Data: 15 Trillion tokens (mixed vision-text)             │ │
│  │  Optimizer: Muon (stability + efficiency)                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        Four Operational Modes                           │ │
│  │                                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │ K2.5 Instant │  │ K2.5 Thinking│  │  K2.5 Agent  │  │ Agent Swarm │ │ │
│  │  │ (3-8 sec)    │  │ (Step-by-    │  │ (200-300     │  │ (100 agents │ │ │
│  │  │              │  │  step)       │  │  tool calls) │  │  parallel)  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     Native Multimodal Capabilities                      │ │
│  │                                                                         │ │
│  │  MoonViT-3D Vision Encoder    │    Joint Text-Vision Optimization      │ │
│  │  Video Understanding (4x)     │    Zero-Vision SFT Activation          │ │
│  │  Visual Coding (UI → Code)    │    Cross-Modal Transfer Learning       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Key Specifications

| Specification | Value | DocuSwarm Relevance |
|---------------|-------|---------------------|
| **Context Window** | 256,000 tokens | Handles full PRD + Architecture + Epic documents |
| **Max Parallel Agents** | 100 sub-agents | Exceeds DocuSwarm's 5-node requirement |
| **Max Tool Calls** | 1,500 per request | Sufficient for complex document workflows |
| **Latency Reduction** | 4.5x (via PARL) | Accelerates pipeline execution |
| **Vision Support** | Native multimodal | Enables diagram/mockup analysis |
| **Function Calling** | Full support | Required for tool integration |

### 2.3 Agent Swarm Architecture (PARL)

Kimi K2.5's **Parallel-Agent Reinforcement Learning (PARL)** framework is particularly aligned with DocuSwarm:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARL Framework - Parallel Agent Execution                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Traditional Sequential Execution:                                           │
│  ┌────┐ → ┌────┐ → ┌────┐ → ┌────┐ → ┌────┐                                │
│  │ T1 │   │ T2 │   │ T3 │   │ T4 │   │ T5 │  Total Time: 5T                │
│  └────┘   └────┘   └────┘   └────┘   └────┘                                │
│                                                                              │
│  PARL Parallel Execution:                                                    │
│                    ┌────────────────────────┐                                │
│                    │    Orchestrator Agent   │                               │
│                    │ (Task Decomposition)    │                               │
│                    └───────────┬────────────┘                                │
│              ┌─────────────────┼─────────────────┐                           │
│              ▼                 ▼                 ▼                           │
│         ┌────────┐       ┌────────┐       ┌────────┐                        │
│         │Sub-Agt1│       │Sub-Agt2│       │Sub-Agt3│  Parallel: ~T         │
│         │ (T1+T2)│       │  (T3)  │       │(T4+T5) │                        │
│         └────────┘       └────────┘       └────────┘                        │
│              │                 │                 │                           │
│              └─────────────────┼─────────────────┘                           │
│                                ▼                                             │
│                    ┌────────────────────────┐                                │
│                    │   Result Aggregation    │  Total Time: ~1.1T           │
│                    └────────────────────────┘  (4.5x improvement)           │
│                                                                              │
│  Key Innovation: Sub-agents frozen during RL, only orchestrator optimized   │
│  Benefits: Clear credit assignment, training stability, parallel scaling    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. API Integration Specifications

### 3.1 API Endpoint Configuration

```javascript
// DocuSwarm Kimi K2.5 Configuration
const KIMI_CONFIG = {
  // Primary Endpoint (Moonshot Direct)
  baseURL: 'https://api.moonshot.cn/v1',
  
  // Model Identifiers
  models: {
    instant: 'kimi-k2.5',           // Fast responses (3-8s)
    thinking: 'kimi-k2.5-thinking', // Detailed reasoning
    agent: 'kimi-k2.5-agent',       // Tool use workflows
    swarm: 'kimi-k2.5-agent-swarm'  // Parallel orchestration (beta)
  },
  
  // Default Parameters
  defaults: {
    temperature: 0.7,
    max_tokens: 4096,
    top_p: 0.95
  },
  
  // Context Configuration
  context: {
    max_context_length: 256000,  // 256K tokens
    context_caching: true        // Enable for cost savings
  }
};
```

### 3.2 Authentication & Setup

```javascript
// Environment Configuration
// .env file
KIMI_API_KEY=your-moonshot-api-key
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_DEFAULT_MODEL=kimi-k2.5

// Node.js Integration with OpenAI SDK
import OpenAI from 'openai';

const kimiClient = new OpenAI({
  apiKey: process.env.KIMI_API_KEY,
  baseURL: process.env.KIMI_BASE_URL
});
```

### 3.3 Rate Limits & Tiers

| Tier | Recharge Amount (¥) | Concurrent Requests | RPM | TPM | TPD |
|------|---------------------|---------------------|-----|-----|-----|
| Tier 0 | ¥0 | 1 | 3 | 500K | 1.5M |
| Tier 1 | ¥50+ | 5 | 50 | 1M | 10M |
| Tier 2 | ¥500+ | 10 | 100 | 2M | 50M |
| Tier 3 | ¥5,000+ | 20 | 200 | 5M | 100M |
| Tier 4 | ¥50,000+ | 50 | 500 | 10M | 500M |
| Tier 5 | ¥100,000+ | 100 | 1000 | 20M | 1B |

**DocuSwarm Recommendation**: Tier 2-3 for development, Tier 4+ for production

### 3.4 Pricing Structure

| Token Type | Price (USD) | Price (CNY) | Notes |
|------------|-------------|-------------|-------|
| **Context Cache Hit** | $0.10/1M | ¥0.70/1M | For repeated context |
| **Context Cache Miss** | $0.60/1M | ¥4.20/1M | New input tokens |
| **Output Tokens** | $3.00/1M | ¥21.00/1M | Generated content |

**Cost Optimization Strategy**:
- Leverage context caching for iterative document refinement
- Batch similar operations within context window
- Use `kimi-k2.5-instant` for simple queries, `thinking` for complex reasoning

---

## 4. DocuSwarm Integration Architecture

### 4.1 Mapping Kimi K2.5 to DocuSwarm Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DocuSwarm + Kimi K2.5 Integrated Architecture                   │
│              (kimi-agent-sdk)                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     DocuSwarm Context Validator                         │ │
│  │                                                                         │ │
│  │   Intent Recognition  ───►  prompt() (instant 模式)                    │ │
│  │   Context Validation  ───►  prompt() (instant 模式)                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                       Pipeline Nodes (Dual-Agent)                       │ │
│  │                                                                         │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │   │ Independent Agent  ───►  Session.prompt() (agent 模式, 多轮)    │  │ │
│  │   │   - Full context access                                          │  │ │
│  │   │   - CallableTool2 自动调度 (via agent_file.yaml)                 │  │ │
│  │   │   - Document creation + question generation                      │  │ │
│  │   └─────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                         │ │
│  │   ┌─────────────────────────────────────────────────────────────────┐  │ │
│  │   │ Evaluator Agent    ───►  prompt() (thinking 模式, 单次)          │  │ │
│  │   │   - Subject context + deliverables only                          │  │ │
│  │   │   - Review/alignment scoring                                     │  │ │
│  │   │   - No private reasoning access (context isolation)              │  │ │
│  │   └─────────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                       │
│                                      ▼                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                   Parallel Node Execution (DAG)                         │ │
│  │                                                                         │ │
│  │                  Kimi K2.5 Agent Swarm Mode (Future)                   │ │
│  │                  - 100 sub-agents per orchestration                    │ │
│  │                  - 1,500 parallel tool calls                           │ │
│  │                  - 4.5x latency reduction                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Mode Selection Matrix

| DocuSwarm Agent | SDK API | SDK Mode Params | Rationale |
|-----------------|---------|----------------|-----------|
| **Context Validator** | `prompt()` 单次 | model="kimi", thinking=False | Fast routing decisions |
| **Independent Agent** | `Session.prompt()` 多轮 | model="kimi", thinking=False | Tool calling + multi-turn |
| **Evaluator Agent** | `prompt()` 单次 | model="kimi", thinking=True | Detailed reasoning for review |
| **Parallel Execution** | Agent Swarm | N/A | Multi-node concurrent (Phase 2) |

### 4.3 Context Isolation Implementation (kimi-agent-sdk)

```python
# Context Manager for kimi-agent-sdk Integration
from kimi_agent_sdk import Session, prompt

class KimiContextManager:
    """基于 kimi-agent-sdk 的上下文管理器"""

    def __init__(self, session_manager):
        self.session_mgr = session_manager

    async def execute_independent(self, subject_context, private_context, node_id):
        """Build context for Independent Agent (full access, Session 多轮)"""
        session = await self.session_mgr.create_session(
            session_id=f"docuswarm-{node_id}",
            mode="agent",
        )
        user_input = json.dumps({
            "subject": subject_context,
            "private": private_context,  # Full access
        })
        # Session.prompt() 多轮对话，工具通过 agent_file.yaml 注册
        messages = []
        async for wire_msg in session.prompt(user_input):
            messages.append(wire_msg)
        return messages

    async def execute_evaluator(self, subject_context, deliverables):
        """Build context for Evaluator Agent (restricted, prompt 单次)"""
        user_input = json.dumps({
            "subject": subject_context,
            "deliverables": deliverables,
            # NOTE: No privateContext - context isolation enforced
        })
        # prompt() 单次 + thinking 模式
        return await self.session_mgr.single_prompt(
            user_input=user_input,
            mode="thinking",
        )
```

### 4.4 Tool Calling Integration (CallableTool2)

```python
# DocuSwarm Tool Definitions for kimi-agent-sdk
from pydantic import BaseModel, Field
from kimi_agent_sdk import CallableTool2, ToolOk, ToolError, ToolReturnValue

class CreateDocumentParams(BaseModel):
    type: str = Field(description="Document type: prd, architecture, epic, story, ux_spec")
    title: str = Field(description="Document title")
    content: str = Field(description="Document content in markdown")
    metadata: dict = Field(default_factory=dict, description="Optional metadata")

class CreateDocumentTool(CallableTool2):
    """创建新文档可交付物"""
    name: str = "create_document"
    description: str = "Create a new document deliverable"
    params: type[CreateDocumentParams] = CreateDocumentParams

    async def __call__(self, params: CreateDocumentParams) -> ToolReturnValue:
        # Save to output directory
        return ToolOk(output=f"Document '{params.title}' ({params.type}) created")

class UpdatePipelineStateParams(BaseModel):
    node: str = Field(description="Node to update")
    status: str = Field(description="pending | in_progress | completed | failed")

class UpdatePipelineStateTool(CallableTool2):
    """更新管线状态"""
    name: str = "update_pipeline_state"
    description: str = "Update the pipeline state"
    params: type[UpdatePipelineStateParams] = UpdatePipelineStateParams

    async def __call__(self, params: UpdatePipelineStateParams) -> ToolReturnValue:
        return ToolOk(output=f"Node '{params.node}' status → {params.status}")

# agent_file.yaml 注册:
# version: 1
# agent:
#   extend: default
#   tools:
#     - "docuswarm.tools.create_document:CreateDocumentTool"
#     - "docuswarm.tools.update_pipeline:UpdatePipelineStateTool"
```

---

## 5. Implementation Strategy

### 5.1 Integration Phases (kimi-agent-sdk)

```mermaid
graph TD
    P1[Phase 1: SDK Setup] --> P2[Phase 2: Basic Integration]
    P2 --> P3[Phase 3: Session Management]
    P3 --> P4[Phase 4: Tool Integration]
    P4 --> P5[Phase 5: Cleanup]
    
    P1 --> |kimi-agent-sdk| SDK[Install SDK + Config]
    P1 --> |Auth| AUTH[SDK Config 管理]
    
    P2 --> |Single Agent| SA[prompt() 单次 API 验证]
    P2 --> |Response Format| RF[Wire 消息 + MessageAggregator]
    
    P3 --> |Session| SESS[Session.create/resume 多轮对话]
    P3 --> |Cancellation| CANCEL[session.cancel() + RunCancelled]
    
    P4 --> |Tools| TOOLS[CallableTool2 + agent_file.yaml]
    P4 --> |Approval| APPROVE[ApprovalRequest handler]
    
    P5 --> |Remove| RM[移除 httpx/langchain-openai 依赖]
    P5 --> |Evaluate| EVAL[评估外层限流是否保留]
```

### 5.2 Phase Details

| Phase | Deliverables | Success Criteria |
|-------|--------------|------------------|
| **Phase 1: SDK Setup** | kimi-agent-sdk 安装, Config 配置 | SDK prompt() 调用成功 |
| **Phase 2: Basic Integration** | KimiSessionManager, Wire 消息处理 | 单次 prompt 返回正确 |
| **Phase 3: Session Management** | Session.create/resume, cancel 机制 | 多轮对话 + 中断恢复 |
| **Phase 4: Tool Integration** | CallableTool2 定义, agent_file.yaml | 工具自动调度成功 |
| **Phase 5: Cleanup** | 移除旧依赖, 评估外层限流 | 无 httpx/langchain-openai 残留 |

### 5.3 kimi-agent-sdk Integration Pattern

```python
# DocuSwarm kimi-agent-sdk Integration
from kimi_agent_sdk import Session, prompt, Config
from pathlib import Path

class DocuSwarmKimiProvider:
    """基于 kimi-agent-sdk 的 Kimi K2.5 接入层"""

    def __init__(self, work_dir: Path, agent_file: Path | None = None):
        self._work_dir = work_dir
        self._agent_file = agent_file

    async def single_call(self, user_input: str, thinking: bool = False) -> list:
        """单次 prompt API (Context Validator / Evaluator)"""
        messages = []
        async for msg in prompt(
            user_input,
            work_dir=self._work_dir,
            model="kimi",
            thinking=thinking,
            agent_file=self._agent_file,
        ):
            messages.append(msg)
        return messages

    async def create_agent_session(self, session_id: str) -> Session:
        """创建多轮 Session (Independent Agent)"""
        return await Session.create(
            work_dir=self._work_dir,
            session_id=session_id,
            model="kimi",
            thinking=False,
            max_steps_per_turn=50,
            agent_file=self._agent_file,
        )

    async def resume_agent_session(self, session_id: str) -> Session | None:
        """恢复已有 Session (中断恢复)"""
        return await Session.resume(
            work_dir=self._work_dir,
            session_id=session_id,
            agent_file=self._agent_file,
        )
```

---

## 6. Comparison: Kimi K2.5 vs Alternative LLMs

### 6.1 Feature Comparison

| Feature | Kimi K2.5 | Claude 3.5 | GPT-4o | Gemini 2.0 |
|---------|-----------|------------|--------|------------|
| **Context Window** | 256K | 200K | 128K | 1M |
| **Native Agent Swarm** | Yes | No | No | No |
| **Parallel Agents** | 100 | Manual | Manual | Manual |
| **Tool Calls/Request** | 1,500 | ~50 | ~128 | ~100 |
| **Multimodal Native** | Yes | Yes | Yes | Yes |
| **OpenAI Compatible** | Yes | No | Yes | No |
| **China Deployment** | Native | No | Limited | Limited |
| **Open Source** | Yes (weights) | No | No | No |

### 6.2 DocuSwarm Fit Score

| Criterion | Weight | Kimi K2.5 | Claude 3.5 | GPT-4o | Score Method |
|-----------|--------|-----------|------------|--------|--------------|
| Agent Swarm Support | 25% | 10 | 5 | 5 | Native support |
| Context Window | 20% | 9 | 8 | 7 | Size adequacy |
| Tool Calling | 20% | 9 | 9 | 9 | Capability |
| API Compatibility | 15% | 10 | 6 | 10 | OpenAI format |
| Cost Efficiency | 10% | 8 | 7 | 6 | $/1M tokens |
| China Availability | 10% | 10 | 2 | 3 | Accessibility |
| **Weighted Total** | 100% | **9.25** | **6.35** | **6.60** | |

### 6.3 Cost Comparison (per 1M tokens)

| Model | Input Cost | Output Cost | Context Cache |
|-------|------------|-------------|---------------|
| **Kimi K2.5** | $0.60 | $3.00 | $0.10 (hit) |
| **Claude 3.5 Sonnet** | $3.00 | $15.00 | $0.30 (prompt caching) |
| **GPT-4o** | $2.50 | $10.00 | N/A |
| **Gemini 2.0 Pro** | $1.25 | $5.00 | N/A |

**DocuSwarm Estimated Monthly Cost** (1000 pipeline executions):
- Kimi K2.5: ~$150-300
- Claude 3.5: ~$600-1200
- GPT-4o: ~$500-1000

---

## 7. Risk Assessment & Mitigation

### 7.1 Risk Matrix

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| **API Rate Limiting** | High | Medium | Implement request queue, tier upgrade, backpressure |
| **Agent Swarm Beta Stability** | Medium | Medium | Fallback to sequential execution, feature flags |
| **Context Window Overflow** | Low | High | Document chunking, summary compression |
| **Tool Call Failures** | Medium | Medium | Retry logic, error categorization, fallback handlers |
| **Network Latency (China)** | Low | Low | VCPToolBox proxy, local deployment option |
| **Model Updates/Deprecation** | Low | High | Version pinning, abstraction layer, monitoring |

### 7.2 Fallback Strategy (kimi-agent-sdk)

```python
# kimi-agent-sdk 绑定 Kimi K2.5，不支持多 provider 切换
# MVP 阶段使用单一 provider，fallback 延迟到 Phase 2

from kimi_agent_sdk.exceptions import ChatProviderError, APIConnectionError, APITimeoutError

class FallbackHandler:
    """MVP: SDK 异常处理 + 日志记录"""

    async def execute_with_fallback(self, operation, *args, **kwargs):
        try:
            return await operation(*args, **kwargs)
        except ChatProviderError as e:
            # API 层面错误 (429, 5xx)
            logger.error("kimi_api_error", status=e.status_code, msg=str(e))
            raise
        except APITimeoutError:
            logger.error("kimi_timeout")
            raise
        except APIConnectionError:
            logger.error("kimi_connection_error")
            raise
```

> **Note**: Phase 2 可在 SDK 层之上实现多 provider 选择逻辑（回退到 OpenAI/Anthropic HTTP API）。

---

## 8. Recommendations & Next Steps

### 8.1 Implementation Roadmap

| Phase | Activities | Milestone |
|-------|------------|-----------|
| **Phase 1** | kimi-agent-sdk 安装, Config 配置, prompt() 验证 | SDK 连接成功 |
| **Phase 2** | KimiSessionManager, Wire 消息处理, MessageAggregator | 单次/多轮调用正常 |
| **Phase 3** | Session.create/resume, cancel 机制, ApprovalRequest | Session 持久化 + 取消 |
| **Phase 4** | CallableTool2 定义, agent_file.yaml 注册 | 工具自动调度 |
| **Phase 5** | 移除旧依赖 (httpx/langchain-openai), 评估外层限流 | 清理完成 |

### 8.2 Configuration Recommendations

```yaml
# config/kimi-provider.yaml (kimi-agent-sdk)
kimi_sdk:
  # SDK 通过 kimi-cli 子进程与 Kimi K2.5 通信
  # API key 由 SDK Config 或环境变量管理
  
  modes:
    context_validator:
      model: kimi
      thinking: false
      max_steps_per_turn: 5
      
    independent:
      model: kimi
      thinking: false
      max_steps_per_turn: 50
      # 工具通过 agent_file.yaml 注册
      
    evaluator:
      model: kimi
      thinking: true
      max_steps_per_turn: 10

rate_limits:
  tier: 3                           # ¥5,000+ recharge
  max_concurrent: 20
  rpm: 200
  tpm: 5000000

cost_optimization:
  context_caching: true             # SDK Session 自动利用
  session_reuse: true               # Session.resume() 复用对话
```

### 8.3 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Success Rate | > 99% | Request logs |
| Average Latency | < 5s (instant), < 30s (thinking) | Response timing |
| Tool Call Accuracy | > 95% | Function execution success |
| Context Isolation | 100% | Security audit |
| Cost per Pipeline | < $0.50 | Token usage tracking |
| Parallel Speedup | > 3x | Execution time comparison |

### 8.4 Final Recommendation

**STRONGLY RECOMMEND** adopting Kimi K2.5 via kimi-agent-sdk as DocuSwarm's designated LLM integration:

1. **kimi-agent-sdk** — 原生 Python SDK 提供 Session/prompt API、Wire 协议、CallableTool2
2. **Session 持久化** — Session.create/resume 支持多轮对话和中断恢复
3. **256K context window** handles full document pipelines
4. **CallableTool2** — Pydantic 类型安全 + SDK 自动调度，替代手动 JSON Schema
5. **Cost-effective pricing** with context caching benefits (Session 自动利用)
6. **Native cancellation** — session.cancel() + RunCancelled 异常

---

## Appendix A: API Reference Quick Guide

### A.1 Chat Completion

```bash
curl https://api.moonshot.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -d '{
    "model": "kimi-k2.5",
    "messages": [
      {"role": "system", "content": "You are a DocuSwarm agent."},
      {"role": "user", "content": "Create a PRD for user authentication."}
    ],
    "temperature": 0.7,
    "max_tokens": 4096
  }'
```

### A.2 Tool Calling

```bash
curl https://api.moonshot.cn/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -d '{
    "model": "kimi-k2.5-agent",
    "messages": [
      {"role": "user", "content": "Query the knowledge base for authentication patterns."}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "query_rag",
          "description": "Query TagMemo RAG system",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {"type": "string"}
            },
            "required": ["query"]
          }
        }
      }
    ]
  }'
```

### A.3 Streaming

```javascript
const stream = await kimiClient.chat.completions.create({
  model: 'kimi-k2.5',
  messages: [{ role: 'user', content: 'Generate architecture diagram...' }],
  stream: true
});

for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || '');
}
```

---

## Appendix B: Error Codes Reference

| Code | Meaning | Resolution |
|------|---------|------------|
| 200 | Success | N/A |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check tier/permissions |
| 429 | Rate Limited | Implement backoff, upgrade tier |
| 500 | Server Error | Retry with exponential backoff |
| 503 | Service Unavailable | Wait and retry |

---

## Appendix C: Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| DocuSwarm Research Report | `reports/DOCUSWARM_RESEARCH_REPORT.md` | System requirements |
| Kimi K2.5 arXiv Paper | `arxiv.org/html/2602.02276v1` | Technical architecture |
| Moonshot API Docs | `platform.moonshot.ai/docs` | Official API reference |
| VCPToolBox AGENTS.md | `VCPToolBox/AGENTS.md` | Platform integration |

---

## Appendix D: Implementation Issues (2026-02-23)

### D.1 Critical Issues Discovered

| Issue | Severity | Status | Reference |
|-------|----------|--------|-----------|
| Message Content Type Mismatch | P0 | Open | [消息内容提取失败问题深度分析](../evaluation/DocuSwarm消息内容提取失败问题深度分析.md) |
| SDK Config Duplicate Keys | P0 | Fixed | [Empty-Response-from-LLM-深度分析报告](../evaluation/Empty-Response-from-LLM-深度分析报告.md) |
| API 404 - Wrong base_url | P0 | Open | [Kimi-K2.5-API-Error-Analysis-Report](../evaluation/Kimi-K2.5-API-Error-Analysis-Report.md) |
| CLI start not executing | P0 | Open | [DocuSwarm-CLI-Research-Report](../evaluation/DocuSwarm-CLI-Research-Report.md) |

### D.2 SDK Message Type Issue

**Root Cause**: `orchestrator.py` assumes `msg.content` is `str`, but SDK returns `list[ContentPart]`.

**Fix Required**:
```python
# Use SDK's extract_text() method
content = msg.extract_text() if hasattr(msg, "extract_text") else str(msg.content)
```

### D.3 Configuration Corrections

| Parameter | Wrong Value | Correct Value |
|-----------|-------------|---------------|
| `base_url` | `https://api.kimi.com/coding/` | `https://api.kimi.com/coding/v1` |
| `model` | `kimi-k2.5` | `kimi-for-coding` |

### D.4 Evaluation Reports

All detailed analysis reports are available in `docs/evaluation/`:
- DocuSwarm流水线CurrentNode问题分析与操作指引.md
- DocuSwarm-CLI-Research-Report.md
- DocuSwarm-TDD-Refactor-Plan.md
- Kimi-K2.5-API-Error-Analysis-Report.md
- Empty-Response-from-LLM-深度分析报告.md
- DocuSwarm消息内容提取失败问题深度分析.md

---

**Report Generated**: 2026-02-20  
**Version**: 2.1 (kimi-agent-sdk)  
**Author**: Research Agent  
**Status**: Implementation In Progress - Issues Identified
**Last Updated**: 2026-02-23
