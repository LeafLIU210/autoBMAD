# Provider Coupling Audit Report

## SessionManager Responsibilities
- Construct ClaudeAgentOptions (SDK-specific)
- Create MCP servers
- Generate allowed_tools list
- Inject Skills setting_sources
- Instantiate ClaudeSDKClient
- Register stderr callback
- Process kill fallback

## Direct SDK Imports Outside llm/ Package
- `tools\agent_sdk_capability_auditor.py`
- `tools\architecture_analyzer.py`
- `tools\kimi_message_probe.py`
- `tools\transport_hardening_research_tool.py`
- `tools\winerror5_architecture_research_tool.py`
- `autoBMAD\epic_automation\epic_driver.py`
- `autoBMAD\epic_automation\sdk_wrapper.py`
- `autoBMAD\docuswarm\tools\create_deliverable_sdk.py`
- `autoBMAD\docuswarm\tools\file_tools_sdk.py`
- `autoBMAD\docuswarm\tools\search_tools_sdk.py`
- `autoBMAD\docuswarm\tools\update_context_sdk.py`

## Boundary Violations
### R1-001 — HIGH
**SessionManager carries too many responsibilities**

SessionManager currently handles 7 distinct concerns: Construct ClaudeAgentOptions (SDK-specific), Create MCP servers, Generate allowed_tools list, Inject Skills setting_sources, Instantiate ClaudeSDKClient, Register stderr callback, Process kill fallback. This violates single-responsibility and causes transport failures to propagate directly to every business node.

**Recommendation**: Extract ClaudeOptionsFactory, ClaudeSessionFactory, ClaudeTransportMonitor.


## Recommended Protocol
### AgentRuntime
- **Purpose**: Isolate business nodes from transport details
- **Methods**: preflight, create_session, close_all
### AgentSession
- **Purpose**: Per-session abstraction
- **Methods**: prompt, close