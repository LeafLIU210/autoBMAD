# FastMCP → SDK MCP 迁移验证清单

**项目**: @autoBMAD/docuswarm  
**迁移类型**: FastMCP 到 SDK MCP 格式  
**版本**: 1.0

---

## 前置条件检查

- [ ] Python 环境 >= 3.10
- [ ] claude_agent_sdk 已安装 (`pip show claude_agent_sdk`)
- [ ] 原始 FastMCP 代码已备份到 `.backup/migration/` 目录
- [ ] 测试环境配置完成 (`pytest --version` 正常)

---

## 第一阶段：单元测试验证

### 文件工具测试 (test_file_tools_migration.py)

| 测试ID | 描述 | 状态 | 备注 |
|-------|------|-----|------|
| TEST-001 | create_file_read_server 返回 dict 类型 | ⬜ | |
| TEST-002 | 服务器包含 type/name/instance 键 | ⬜ | |
| TEST-003 | 服务器 type 为 'sdk' | ⬜ | |
| TEST-004 | 服务器名称格式正确 (docuswarm-files-{node_id}) | ⬜ | |
| TEST-005 | read_document 成功读取返回正确格式 | ⬜ | |
| TEST-006 | read_document 拒绝不允许的路径 | ⬜ | |
| TEST-007 | read_document 处理不存在的文件 | ⬜ | |
| TEST-008 | list_documents 非递归模式工作正常 | ⬜ | |
| TEST-009 | list_documents 递归模式工作正常 | ⬜ | |
| TEST-010 | 空 node_id 抛出 ValueError | ⬜ | |
| TEST-011 | 空 allowed_dirs 抛出 ValueError | ⬜ | |
| TEST-012 | 不存在的目录记录警告 | ⬜ | |

**阶段 1 结果**: ___/12 通过

### 搜索工具测试 (test_search_tools_migration.py)

| 测试ID | 描述 | 状态 | 备注 |
|-------|------|-----|------|
| TEST-013 | create_search_server 返回 dict 类型 | ⬜ | |
| TEST-014 | 服务器名称格式正确 (docuswarm-search-{node_id}) | ⬜ | |
| TEST-015 | grep_search 能找到匹配内容 | ⬜ | |
| TEST-016 | grep_search 遵守 max_results 限制 | ⬜ | |
| TEST-017 | glob_search 能找到匹配文件 | ⬜ | |
| TEST-018 | glob_search 支持递归模式 | ⬜ | |

**阶段 2 结果**: ___/6 通过

---

## 第二阶段：集成测试验证

### 会话管理集成 (test_session_manager_integration.py)

| 测试ID | 描述 | 状态 | 备注 |
|-------|------|-----|------|
| TEST-019 | SDK MCP 服务器与 ClaudeAgentOptions 兼容 | ⬜ | |
| TEST-020 | ClaudeSDKClient 能成功连接 | ⬜ | |
| TEST-021 | 工具过滤器返回 dict 类型 | ⬜ | |
| TEST-022 | 工具过滤器返回正确的服务器名称 | ⬜ | |
| TEST-023 | 工具过滤器生成正确的 MCP 工具名 | ⬜ | |

**阶段 3 结果**: ___/5 通过

---

## 第三阶段：端到端测试验证

### 完整流水线测试 (test_end_to_end_pipeline.py)

| 测试ID | 描述 | 状态 | 备注 |
|-------|------|-----|------|
| TEST-024 | 组合服务器能成功创建会话 | ⬜ | |
| TEST-025 | SessionManager 能使用 SDK MCP 创建会话 | ⬜ | |
| TEST-026 | SDK 模式下不使用 FastMCP 对象 | ⬜ | |

**阶段 4 结果**: ___/3 通过

---

## 性能验证

| 测试项 | 目标 | 实际 | 状态 |
|-------|-----|-----|------|
| 会话创建时间 | < 2s | ___s | ⬜ |
| 工具执行延迟 | < 500ms | ___ms | ⬜ |
| 内存使用峰值 | < 200MB | ___MB | ⬜ |

---

## 代码覆盖率

| 模块 | 目标覆盖率 | 实际覆盖率 | 状态 |
|-----|----------|-----------|------|
| file_tools_sdk.py | >= 90% | ___% | ⬜ |
| search_tools_sdk.py | >= 90% | ___% | ⬜ |
| tool_filter_adapter.py | >= 85% | ___% | ⬜ |
| session_manager_sdk.py | >= 80% | ___% | ⬜ |

---

## 回滚准备

- [ ] 原始 FastMCP 代码已备份到 `docs/solution/backup/` 目录
- [ ] 环境变量切换机制已测试 (`DOCUSWARM_USE_SDK_MCP`)
- [ ] 回滚脚本已准备 (`scripts/rollback_migration.sh`)

---

## 文档更新

- [ ] API 文档已更新 (`docs/api/mcp-tools.md`)
- [ ] 部署指南已更新 (`docs/deployment.md`)
- [ ] 故障排查文档已更新 (`docs/troubleshooting.md`)
- [ ] CHANGELOG 已更新

---

## 最终确认

| 检查项 | 状态 | 签名 | 日期 |
|-------|-----|-----|------|
| 所有单元测试通过 (18/18) | ⬜ | | |
| 所有集成测试通过 (5/5) | ⬜ | | |
| 所有端到端测试通过 (3/3) | ⬜ | | |
| 代码审查完成 | ⬜ | | |
| 性能测试通过 | ⬜ | | |
| 文档已更新 | ⬜ | | |
| 回滚方案已验证 | ⬜ | | |

---

## 迁移后验证命令

```bash
# 1. 运行所有测试
pytest docs/solution/test-suite/ -v --tb=short

# 2. 检查测试覆盖率
pytest docs/solution/test-suite/ --cov=autoBMAD.docuswarm --cov-report=term-missing

# 3. 验证无 FastMCP 残留
grep -r "from mcp.server.fastmcp" autoBMAD/docuswarm/ || echo "✓ No FastMCP imports found"

# 4. 验证 SDK MCP 格式
grep -r "create_sdk_mcp_server" autoBMAD/docuswarm/ | wc -l

# 5. 运行集成测试
pytest docs/solution/test-suite/test_session_manager_integration.py -v
```

---

**清单维护者**: ___  
**最后更新**: ___  
**审批人**: ___
