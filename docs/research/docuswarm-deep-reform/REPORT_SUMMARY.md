# 文档创建约束与模板对齐研究 - 执行摘要

**报告编号**: DS-2026-03-06-001  
**研究日期**: 2026-04-06  
**研究状态**: ✅ 完成  
**报告总行数**: 1566行  

---

## 核心问题

DocuSwarm 五个节点（analyst、pm、ux、architect、po）的文档创建需求不同：
- **Analyst、PM、UX**：各需创建1份文档（受限）
- **Architect、PO**：各需创建2-5份相关文档（多文档）

**现状**：系统设计为单文档模式，无法表达多文档约束和结果。

---

## 关键发现

### 1. 当前系统的强点和弱点

**强点**：
- ✅ Validator 通过 file_path/sha256 实现可靠的文件存在性验证
- ✅ LLM 无法伪造有效的 SHA256 哈希
- ✅ 工具调用成为不可绕过的必要步骤

**弱点**：
- ❌ CreateDeliverableTool 是单文档型设计
- ❌ NodeResult 只能返回一个 deliverable 对象
- ❌ node.yaml 无法声明数量约束
- ❌ Validator 无法检查多文档计数

### 2. 三层约束实施方案

| 层级 | 方案A | 方案B | 方案C（推荐） |
|------|--------|---------|------------|
| **配置** | ✓ | ✗ | ✓ |
| **验证** | ✗ | ✗ | ✓ |
| **执行** | ✗ | ✓ | ✓ |
| **向后兼容** | ✓ | ~ | ✓ |
| **集中管理** | ✓ | ~ | ✓ |

**推荐方案 C**：在 Validator 中添加 max_deliverables 规则检查

### 3. 多文档支持的向后兼容包装

```json
// 单文档（现状）
{
  "deliverable": {
    "title": "Report",
    "file_path": "...",
    "sha256": "..."
  }
}

// 多文档（新）- 向后兼容包装
{
  "deliverable": {
    "title": "Deliverables Set",
    "type": "multi-document",
    "documents": [
      { "index": 1, "type": "epic-list", "file_path": "...", "sha256": "..." },
      { "index": 2, "type": "story-prioritization", "file_path": "...", "sha256": "..." }
    ]
  }
}
```

**优点**：
- JSON 结构保持一致
- 现有消费者可自动降级处理
- 可选择采用新格式

---

## 实施路线图

### 阶段划分

| 阶段 | 内容 | 工作量 | 风险 |
|------|------|--------|------|
| **Phase 1-3** | 单文档约束实施 | 3-4 周 | 低 |
| **Phase 4-5** | 多文档支持 | 4-5 周 | 中 |
| **Phase 6** | 文档和培训 | 1 周 | 低 |
| **总计** | 完整方案 | **9.5 周** | - |

### 关键检查点

```
第2周末  ✓ 参数扩展单元测试通过
第4周末  ✓ Validator集成测试通过
第5周末  ✓ 单文档约束端到端测试通过
第7周末  ✓ 多文档工作流（至少PO）可用
第9周末  ✓ 模板对齐和文档完成
```

---

## 主要改动

### 代码改动

**新增参数**（CreateDeliverableParams）：
- `document_index`: 文档在集合中的位置
- `document_total`: 集合中的总文档数
- `document_type`: 文档类型标识

**Validator 增强**：
- 新增 `max_deliverables` 规则
- 支持多文档格式验证
- 每个文档必须有 file_path/sha256

**NodeResult 升级**（向后兼容）：
- 新增便利属性：`is_multi_document`, `all_documents`, `total_word_count`
- 保持现有 deliverable 字段

### 配置文件改动

**node.yaml 扩展**：
```yaml
deliverable:
  max_deliverables: 1              # ← 单文档约束
  required_sections: [...]
```

**新增模板文件**：
- `autoBMAD/docuswarm/templates/architect_templates.yaml`
- `autoBMAD/docuswarm/templates/po_templates.yaml`

---

## 优先级和风险评估

### 优先级

**必做（Phase 1-3）**：
- 为 analyst、pm、ux 实施单文档约束
- 理由：低风险、快速收益、基础必要

**可做（Phase 4-5）**：
- 为 architect、po 支持多文档
- 理由：中等风险、可分阶段试验

**配套（Phase 6）**：
- 模板对齐和文档
- 理由：非阻塞、提升体验

### 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 向后兼容性破裂 | 高 | 采用包装方式 |
| Validator 复杂度增加 | 中 | 分离验证逻辑 |
| LLM 混淆新参数 | 中 | System Prompt 清晰指导 |
| 数据库查询性能 | 低 | 限制文档数量 |

---

## 关键成功因素

1. **System Prompt 的清晰指导**
   - 明确告诉 LLM 哪些节点需创建多少份文档
   - 提供 JSON 格式示范

2. **Validator 的渐进式扩展**
   - 不一次性修改所有逻辑
   - 新旧验证规则并行

3. **充分的测试覆盖**
   - 单文档、多文档、约束超限场景
   - 迭代和重试场景

4. **文档和培训**
   - API 变化清晰说明
   - 开发者理解新能力

---

## 建议立即行动项

### 短期（第1-2周）

- [ ] 启动 Phase 1 参数扩展工作
- [ ] 制定详细的工程计划表
- [ ] 组织团队培训和知识对齐

### 中期（第2-6周）

- [ ] 完成 Phase 1-3（单文档约束）
- [ ] 收集反馈和教训
- [ ] 准备 Phase 4-5 详细设计

### 长期（第6-9周）

- [ ] 执行 Phase 4-5（多文档支持）
- [ ] 进行模板对齐（Phase 5）
- [ ] 文档和知识沉淀

---

## 相关文件

| 文件 | 内容 | 行数 |
|------|------|------|
| `03-document-creation-constraints.md` | 完整研究报告 | 1566 |
| `README.md` | 报告导航和使用指南 | 70 |
| `REPORT_SUMMARY.md` | 本文件（执行摘要） | - |

---

## 下一步

1. **提交评审**：向架构和技术委员会提交完整报告
2. **优先级确认**：确认 Phase 1-3 为必做，Phase 4-5 为可做
3. **工程规划**：启动详细的工程计划制定
4. **团队对齐**：组织全队同步和培训

---

**报告完成时间**: 2026-04-06  
**预期评审时间**: 2026-04-08  
**预期实施启动**: 2026-04-09
