# 五节点独立 Agent 任务重构方案研究报告

**报告日期**：2026-04-06 | **状态**：待审批 | **基础**：Task 1 - Skills 引入方案研究

---

## 1. 概述

### 1.1 研究目标
研究5个节点（Analyst、PM、UX、Architect、PO）如何将当前通用任务重构为对应BMAD技能引用，建立从node.yaml任务配置到SDK Skill调用的完整映射。

### 1.2 节点与Skill映射表
| 节点 | 当前task.name | 目标Skill | 匹配度 |
|------|-------------|---------|------|
| Analyst | create-business-analysis-report | bmad-product-brief | ⚠️ 需重构 |
| PM | create-product-requirements-document | bmad-create-prd | ✅ 对齐 |
| UX | create-ux-design-specification | bmad-create-ux-design | ✅ 对齐 |
| Architect | create-system-architecture-document | bmad-create-architecture | ✅ 对齐 |
| PO | create-epics-and-user-stories | bmad-create-epics-and-stories | ✅ 对齐 |

### 1.3 前置结论
基于Task 1研究，推荐采用**方案C（混合方案）**：SDK原生discovery + system prompt快速参考 + node.yaml whitelist控制。

---

## 2. 当前节点配置分析概览

### 2.1 Analyst节点 - 职责转向分析
**问题**：当前task为"create-business-analysis-report"（业务分析），但目标Skill"bmad-product-brief"是产品概要创建。  
**建议**：将Analyst定位从"数据分析报告"改为"产品简介创建"。

**重构配置**（node.yaml）：
```yaml
task:
  name: create-product-brief
  skill_ref: bmad-product-brief
  role_supplement: 作为产品发现促进者，引导用户理解产品意图，而非扫描工件。
```

**persona.json更新要点**：
- name: "Mary" (BMAD模板中指定)
- role: 从"Data Analyst"改为"Strategic Business Analyst & Product Discovery Expert"
- communication_style: 添加"treasure_hunter_energy"

### 2.2 PM、UX、Architect、PO节点 - 对齐现有

**PM节点**：配置与Skill高度对齐，主要补强。
- 添加skill_ref: bmad-create-prd
- 补充persona的expertise中的框架（RICE、Jobs-to-be-Done）

**UX、Architect、PO节点**：同样补强而非根本改造。

---

## 3. BMAD Skill工作流对比

| Skill | 工作流阶段 | 配置文件依赖 | 输出规范 |
|-------|----------|----------|--------|
| bmad-product-brief | 5阶段（Discovery-Elicitation-Review-Finalize） | _bmad/bmm/config.yaml | 1-2页executive brief |
| bmad-create-prd | Step-file架构（Just-In-Time加载） | _bmad/bmm/config.yaml | PRD markdown |
| bmad-create-ux-design | 微文件架构（Append-only构建） | _bmad/bmm/config.yaml | UX设计规范 |
| bmad-create-architecture | 协作式微文件（用户批准驱动） | _bmad/bmm/config.yaml | 架构文档 |
| bmad-create-epics-and-stories | Step-file（先决条件验证） | _bmad/bmm/config.yaml | Epics + Stories |

**关键观察**：所有Skills共享配置文件模式，依赖{project-root}/_bmad/bmm/config.yaml。

---

## 4. 任务重构方案 - 5个节点配置

### 4.1 Analyst节点 - 核心改造

```yaml
# node.yaml改造
task:
  name: create-product-brief
  description: 通过协作发现创建产品简介。
  role_supplement: 作为产品发现促进者，理解产品意图后再分析工件。
  skill_ref: bmad-product-brief  # ← 新增

tools:
  skills:
    sdk_native: true
    whitelist:
      - bmad-product-brief
      - bmad-domain-research
      - bmad-market-research
      - bmad-advanced-elicitation
```

```json
// persona.json主要字段
{
  "name": "Mary",
  "role": "Strategic Business Analyst & Product Discovery Expert",
  "expertise": [
    "Product discovery and market research",
    "Porter's Five Forces and SWOT analysis",
    "Requirements elicitation"
  ]
}
```

### 4.2 PM、UX、Architect、PO节点 - 配置补强

每个节点的改造遵循类似模式：
1. 在task中添加skill_ref字段
2. 在node.yaml中添加tools.skills配置段（whitelist）
3. 在persona.json中补充name、增强expertise
4. 调整evaluator.yaml权重以适应新Skill

---

## 5. node.yaml → Skill调用的机制设计

### 5.1 新增task.skill_ref字段

```python
@dataclass
class NodeTaskConfig:
    name: str
    description: str = ""
    role_supplement: str = ""
    skill_ref: str | None = None  # ← 新增可选字段
```

### 5.2 loader.py改造

在`_build_node_config()`中解析skill_ref：
```python
task_config = NodeTaskConfig(
    name=task_data["name"],
    description=task_data.get("description", ""),
    role_supplement=task_data.get("role_supplement", ""),
    skill_ref=task_data.get("skill_ref")  # ← 新增
)
```

### 5.3 independent.py中的Skill调用

集成SkillInjector到system prompt：
```python
async def _call_llm_with_prompts(...):
    node_config = NodeLoader.load(self.node_id)
    
    # 构建Skill快速参考并注入
    skills_quick_ref = SkillInjector.build_skills_quick_reference(
        node_id=self.node_id,
        node_skill_config=node_config.tool_permissions.skills,
    )
    
    if skills_quick_ref:
        system_prompt_append += "\n\n" + skills_quick_ref
    
    # 创建Session并调用LLM
```

### 5.4 SessionManager启用SDK Skills

```python
def _create_options(self, mode: str, yolo: bool) -> ClaudeAgentOptions:
    options_dict = {
        "cwd": self._cwd,
        "setting_sources": ["project"],  # ← 启用.claude/skills/自动发现
        "allowed_tools": self._build_allowed_tools(),
    }

def _build_allowed_tools(self) -> list[str]:
    tools = ["Skill"]  # ← 添加SDK原生Skill工具
    # ... 其他工具
    return tools
```

---

## 6. 代码改动清单

### P0级改动（必需）

| 文件 | 改动 | 优先级 |
|------|------|--------|
| autoBMAD/nodes/loader.py | NodeTaskConfig添加skill_ref；NodeToolPermissions添加skills | P0 |
| autoBMAD/docuswarm/llm/session_manager.py | 启用setting_sources + "Skill"工具 | P0 |
| autoBMAD/docuswarm/prompts/skill_injector.py | 新增文件（SkillInjector类） | P0 |
| autoBMAD/docuswarm/agents/independent.py | 集成SkillInjector到system prompt | P0 |
| nodes/*/node.yaml（5个） | 更新task字段+skills配置 | P0 |
| nodes/*/persona.json（5个） | 添加name、增强expertise | P0 |
| tests/test_skills_integration.py | 新增集成测试 | P1 |

---

## 7. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| Analyst职责转换破裂流程 | 中 | 高 | 保持向后兼容；社内通知；作为试点 |
| SDK Setting Sources加载失败 | 中 | 高 | 验证cwd和.claude/skills/结构；fallback日志 |
| skill_ref未被识别 | 低 | 高 | 完整单元测试；clear error messages |
| Claude选错Skill | 中 | 中 | 优化description字段；定期审计 |

---

## 8. 实施路线图

**Phase 1（2天）**：代码框架改造
- 扩展loader.py、新增skill_injector.py
- 更新session_manager.py、independent.py
- 单元测试

**Phase 2（1.5天）**：节点配置迁移
- 更新5个节点的node.yaml、persona.json、evaluator.yaml
- 验证所有配置有效

**Phase 3（1.5天）**：集成测试与文档
- 端到端集成测试
- 编写使用指南和troubleshooting文档

**Phase 4（1天）**：灰度部署
- 测试环境验证
- 生产灰度部署和监控

**总计**：5-6个工作日

---

## 9. 建议与后续优化

### 短期（1-3个月）
- 完善SKILL.md的description字段
- 建立Skill编写规范和模板
- 实施自动验证脚本

### 中期（3-6个月）
- 支持Skill版本管理
- 开发Skill管理工具
- 集成性能基准测试

### 长期（6个月+）
- 完全迁移到SDK原生方式
- 实施Skill推荐系统
- 社区Skill库共享

---

## 10. 参考资源

- **前置报告**：`01-skills-introduction-mechanism.md`（Skills引入方案）
- **SDK文档**：`autoBMAD/agentdocs/22_skills.md`（SDK Skills机制）
- **系统架构**：`docs/stories/29.6.md`（Four-Layer Architecture）
- **BMAD模板**：`_bmad/bmm/agents/`（Agent定义模板）

---

**报告完成**：2026-04-06  
**下一步**：实施Phase 1代码改动
