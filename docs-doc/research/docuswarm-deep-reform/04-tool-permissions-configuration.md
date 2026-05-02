# 工具权限全面开放方案研究报告

## 1. 概述

### 研究目标

本报告研究 DocuSwarm 项目中所有节点的独立 Agent 和评估 Agent 如何全面配置 5 个关键工具的权限，实现从当前受限访问升级到全面开放的工具权限体系。

### 背景与意义

当前 DocuSwarm 的 5 个节点（analyst、pm、ux、architect、po）都未在 node.yaml 中配置 tools 字段，导致仅有 create_deliverable 工具始终可用，其他 4 个工具不可见。全面开放将增强 Agent 上下文理解能力，同时维持安全隔离。

---

## 2. 当前工具权限体系分析

### 2.1 tool_registry.py 的工具注册机制

**关键特点**:
- 全局单例注册器 (_global_registry)
- register() 方法注册工具到 _tools 字典
- 与权限管理无关，提供发现和执行接口
- 工具定义包含: name, func, description, schema

**权限管理由 NodeToolFilter 和 SessionManager 处理，registry 保持不变。**

### 2.2 node.yaml 中 tools 字段解析流程

#### YAML 配置格式

所有 5 节点均配置:
```yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/", "docs/research/"]
  search_permissions:
    search_dirs: ["docs/"]
```

#### 解析流程 (loader.py)

1. **NodeLoader.load()** (第 200-250 行): 读取 node.yaml，调用 _build_node_config()
2. **工具权限提取** (第 432-447 行): 从 tools 字段构建 NodeToolPermissions 对象
3. **数据类结构**: NodeToolPermissions / NodeFilePermissions / NodeSearchPermissions

### 2.3 independent.py 中的工具加载链

**关键流程**:
1. execute_with_input() → NodeLoader.load(node_id)
2. 提取 file_dirs / search_dirs (绝对路径)
3. 构建 NodeToolPermissions
4. 传递给 SessionManager (第 787-818 行)
5. SessionManager._create_options() → NodeToolFilter.create_mcp_servers()
6. 返回 MCP 服务器 + allowed_tools 列表
7. 传递给 ClaudeAgentOptions

**结果**: IndependentAgent 已完全支持工具权限配置

### 2.4 evaluator.py 中的工具访问

**当前设计**: EvaluatorAgent 是"无工具" Agent
- 不传递 node_id 给 SessionManager
- single_prompt() 不创建 MCP 服务器
- 上下文隔离: 拒绝 private_reasoning 字段
- 专注于评分，不主动访问文件

**理由**: 维持"dumb evaluator" 模式，简化安全验证

### 2.5 当前 5 个节点的配置现状

| 节点 | allowed_builtin_tools | file_read_dirs | search_dirs | 状态 |
|------|----------------------|-------------------|------------|------|
| analyst | ["Read", "Glob"] | docs/, docs/research/ | docs/ | 配置完成 |
| pm | ["Read", "Glob"] | docs/ | docs/ | 配置完成 |
| ux | ["Read", "Glob"] | docs/ | docs/ | 配置完成 |
| architect | ["Read", "Glob"] | docs/ | docs/ | 配置完成 |
| po | ["Read", "Glob"] | docs/ | docs/ | 配置完成 |

**缺失**: create_deliverable 虽未显式配置，但通过 output_dir 参数自动启用

---

## 3. 5 个工具的详细分析

### 3.1 create_deliverable

**参数**: title (必需) / content (必需) / metadata (可选)
**返回**: {file_path, sha256, word_count, section_index, content_type}
**安全模型**:
- 固定输出目录 (output_dir)
- 文件名 slugify (防止目录遍历)
- SHA256 验证 (强制性调用保证)

### 3.2 read_document

**参数**: path / max_size
**返回**: 文件内容 (截断至 50000 字符)
**白名单机制**:
- PathValidator: 路径规范化 + realpath() + 前缀匹配
- ALLOWED_EXTENSIONS: .md, .txt, .yaml, .yml, .json, .py, .js, .ts, .tsx, .jsx
- BLOCKED_EXTENSIONS: .db, .sqlite, .key, .pem, .exe, .dll 等 25 种
- BLOCKED_PATTERNS: .env, .git, node_modules, __pycache__ 等
- 符号链接防护: os.path.realpath()

### 3.3 list_documents

**参数**: directory / recursive / extensions (过滤)
**返回**: 文件路径列表 (绝对路径)
**访问控制**:
- PathValidator 验证目录
- 递归模式: os.walk() + 原地过滤 dirs[:]
- 每个文件再次验证 validate()
- 支持扩展名过滤

### 3.4 grep_search

**参数**: pattern (正则) / path / max_results (默认20, 限制50)
**返回**: {results: [{file, line, content}], total_matches, truncated}
**限制**:
- 正则表达式编译验证
- 跳过二进制文件 (_is_binary_file)
- 跳过 >10MB 文件
- 早期终止优化 (收集足够结果后停止)

### 3.5 glob_search

**参数**: pattern (glob) / path / max_results
**返回**: 文件路径列表
**特点**:
- fnmatch 模式匹配
- 支持 `**` 递归
- 限制 50 条结果
- 防止符号链接跟踪 (followlinks=False)

---

## 4. 全面开放方案设计

### 4.1 node.yaml 配置变更

#### 推荐方案: 所有节点统一全面开放

```yaml
# analyst/node.yaml, pm/node.yaml, ux/node.yaml, architect/node.yaml, po/node.yaml
tools:
  allowed_builtin_tools: ["Read", "Glob"]
  file_permissions:
    allowed_read_dirs: ["docs/"]  # 简化: 根目录覆盖所有子目录
  search_permissions:
    search_dirs: ["docs/"]
```

**优点**: 简化配置、一致性、易维护
**与 PathValidator 兼容**: 目录不需列举所有子目录

### 4.2 tool_registry 变更

**建议**: 保持不变。tool_registry 不负责权限管理。

### 4.3 independent.py 变更

**需要的变更**:
1. 验证权限传递完整性 (增加日志)
2. 系统提示提及所有可用工具
3. 测试用例验证跨目录访问

**验证清单**:
- [ ] node.yaml 含 tools 配置
- [ ] NodeLoader 正确解析
- [ ] SessionManager 传递完整 NodeToolPermissions
- [ ] NodeToolFilter 创建所有 MCP 服务器
- [ ] 系统提示列举所有工具
- [ ] 日志记录工具配置
- [ ] 测试跨目录文件访问

### 4.4 evaluator.py 变更

**建议**: 保持当前无工具设计

**理由**:
- 上下文隔离更易验证
- 评估 Agent 职能是评分，不是收集
- 避免安全风险引入
- 设计更简洁

---

## 5. 安全性评估

### 5.1 多层防御机制

```
Layer 1: PathValidator (节点级)
  - 目录白名单
  - 符号链接解析 (realpath)
  - 前缀匹配检查

Layer 2: 文件类型限制
  - 扩展名白名单 (允许)
  - 扩展名黑名单 (禁止)
  - 大小限制 (50000 字符)

Layer 3: 目录模式阻止
  - .git, .env 等敏感目录
  - node_modules, __pycache__
  - .DS_Store, .svn

Layer 4: 应用级检查
  - 二进制文件检测
  - 编码验证
  - 访问日志
```

### 5.2 潜在漏洞分析

**符号链接绕过**:
```bash
ln -s /etc/passwd /docs/passwd.md
# 防御: realpath() 解析后再检查
```

**目录遍历**:
```bash
read_document("../../../etc/passwd")
# 防御: os.path.abspath() + os.path.realpath()
```

**时间竞争 (TOCTOU)**:
```
# 防御: 每次 open() 前重新验证 (kernel 级安全)
```

### 5.3 上下文隔离评估

**EvaluatorAgent 隔离**:
```python
# isolation.py 严格检查
if "private_reasoning" in context:
    raise ValueError("Context isolation violation")
```

**隔离强度**: ★★★★☆ (4/5)

**缓解措施**:
1. 访问日志 (审计所有文件读取)
2. 速率限制 (防止暴力读取)
3. 权限审计 (定期检查配置)
4. 白名单验证 (拒绝意外字段)

---

## 6. 代码改动清单

### 6.1 必需改动

| 文件 | 改动 | 优先级 |
|------|------|--------|
| analyst/node.yaml | 添加/更新 tools 配置 | P0 |
| pm/node.yaml | 添加/更新 tools 配置 | P0 |
| ux/node.yaml | 添加/更新 tools 配置 | P0 |
| architect/node.yaml | 添加/更新 tools 配置 | P0 |
| po/node.yaml | 添加/更新 tools 配置 | P0 |

### 6.2 可选改动

| 文件 | 改动 | 目的 |
|------|------|------|
| independent.py | 系统提示提及工具 | 用户指导 |
| session_manager.py | 增强权限配置日志 | 调试辅助 |
| tool_filter.py | 增强 MCP 创建日志 | 调试辅助 |

### 6.3 无需改动

- tool_registry.py (权限管理无关)
- evaluator.py (保持无工具设计)
- base.py (基类无变更)
- file_tools.py / search_tools.py (实现不变)
- tool_filter.py (已支持完整权限)
- isolation.py (隔离检查已完整)

---

## 7. 风险评估

### 7.1 实施风险

**低风险**: 
- 配置变更 (不涉及代码逻辑)
- 向后兼容 (现有权限机制完整)
- 回滚简单 (恢复 node.yaml)

**中风险**:
- 广泛文件访问 (增加 Agent 信息收集能力)
- 缓解: PathValidator 白名单充分

### 7.2 安全风险

**已识别风险**:
1. 符号链接攻击: 已防护 (realpath)
2. 目录遍历: 已防护 (规范化 + realpath)
3. 敏感文件泄露: 已防护 (扩展名黑名单)

**新引入风险**: 无显著新风险

### 7.3 运营风险

**风险**: 权限配置错误导致访问控制失效
**缓解**: 
- 权限审计工具
- 访问日志
- 定期权限检查

---

## 8. 实施路线图

### Phase 1: 准备 (1-2 天)

- [ ] 审查本报告，获得批准
- [ ] 准备测试环境
- [ ] 编写测试用例

### Phase 2: 配置变更 (1 天)

- [ ] 更新 5 个 node.yaml 文件
- [ ] 验证 YAML 格式
- [ ] NodeLoader 解析测试

### Phase 3: 系统提示更新 (1 天)

- [ ] 更新 IndependentAgent 系统提示
- [ ] 添加工具使用示例
- [ ] 更新文档

### Phase 4: 测试 (2-3 天)

- [ ] 单元测试: 文件工具
- [ ] 集成测试: Agent + 工具
- [ ] 跨目录访问测试
- [ ] 安全检查: 边界情况

### Phase 5: 监控与调优 (持续)

- [ ] 访问日志分析
- [ ] 性能监测
- [ ] 权限审计
- [ ] 问题跟进

---

## 9. 总结与建议

### 9.1 核心发现

1. **工具权限体系完备**: tool_registry / NodeLoader / SessionManager / NodeToolFilter 完整支持权限管理
2. **全面开放可行**: 现有实现已经支持，仅需配置 node.yaml
3. **安全机制充分**: PathValidator + 多层防御已覆盖主要攻击向量
4. **隔离设计稳健**: EvaluatorAgent "无工具"设计优于赋予权限

### 9.2 建议

**立即实施**:
- 更新 5 个 node.yaml (添加 tools 配置)
- 增强系统提示 (提及工具)
- 添加测试用例

**短期 (1-2 周)**:
- 访问日志审计
- 权限配置验证
- 性能基准测试

**中期 (1-3 月)**:
- 权限审计工具开发
- 安全最佳实践文档
- 定期权限检查流程

### 9.3 后续研究方向

1. **细粒度权限**: 工具级 / 操作级权限控制
2. **速率限制**: 防止工具滥用
3. **敏感内容检测**: 自动检测并阻止访问敏感信息
4. **权限委托**: 支持临时权限提升 (如评估 Agent 临时读取权限)

---

## 附录 A: 工具安全对比

| 工具 | 输入验证 | 路径检查 | 大小限制 | 类型检查 | 风险等级 |
|------|---------|---------|---------|---------|---------|
| create_deliverable | ✓ | ✓ (固定目录) | ✗ | ✓ | 低 |
| read_document | ✓ | ✓ | ✓ (50000) | ✓ | 低 |
| list_documents | ✓ | ✓ | ✓ (递归限制) | ✓ | 低 |
| grep_search | ✓ (正则) | ✓ | ✓ (10MB) | ✓ | 低 |
| glob_search | ✓ (glob) | ✓ | ✓ (50 结果) | ✗ | 低 |

---

## 附录 B: 测试清单

### B.1 单元测试

- [ ] PathValidator: 路径规范化
- [ ] PathValidator: 符号链接解析
- [ ] PathValidator: 前缀匹配
- [ ] read_document: 文件大小截断
- [ ] read_document: 扩展名过滤
- [ ] list_documents: 递归模式
- [ ] grep_search: 正则表达式
- [ ] glob_search: 通配符模式

### B.2 集成测试

- [ ] Agent 工具初始化
- [ ] NodeToolFilter MCP 创建
- [ ] SessionManager 工具配置
- [ ] Independent Agent + 文件工具
- [ ] Independent Agent + 搜索工具
- [ ] 跨目录文件访问
- [ ] 敏感文件阻止

### B.3 安全测试

- [ ] 符号链接攻击 (防护验证)
- [ ] 目录遍历攻击 (防护验证)
- [ ] 扩展名绕过 (防护验证)
- [ ] 大小限制绕过 (防护验证)
- [ ] 权限隔离 (EvaluatorAgent)

---

**报告完成**: 2026-04-06
**研究员**: 研究分析 Agent
**版本**: 1.0
