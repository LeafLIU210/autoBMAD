# TDD-BMM-05: BMM NodeExecutor 重构主实施指南

## 文档信息

| 属性 | 值 |
|------|-----|
| **方案编号** | TDD-BMM-05 |
| **关联研究** | Part 1-5 全部 |
| **优先级** | P0 - Critical |
| **状态** | 待实施 |

---

## 1. 概述

本指南汇总 TDD-BMM-01 至 TDD-BMM-04 的全部内容，提供：
- 完整的实施路线图
- 依赖关系图
- 阶段划分和里程碑
- 回滚策略
- 验收标准

---

## 2. 重构范围总结

### 2.1 涉及的模块

```
autoBMAD/docuswarm/
├── nodes/
│   ├── loader.py              # TDD-01: 配置加载重构
│   ├── analyst/
│   │   ├── node.yaml          # TDD-01: 新增task块
│   │   ├── persona.json       # TDD-02: BMM角色上下文
│   │   └── evaluator.yaml     # TDD-02: 描述微调
│   ├── pm/                    # 同上
│   ├── ux/                    # 同上
│   ├── architect/             # 同上
│   └── po/                    # 同上
├── agents/
│   ├── persona.py             # TDD-02: communication_style
│   └── independent.py         # TDD-02: System Prompt重构
├── pipeline/
│   └── graph.py               # TDD-03: 移除废弃函数
├── templates/                 # TDD-03: 整体移除
└── (其他文件保持不变)
```

### 2.2 不涉及的模块

以下模块**不受**本次重构影响：
- `storage/files.py` - 交付物保存逻辑不变
- `storage/checkpoints.py` - 检查点管理不变
- `context/filter.py` - 上下文过滤逻辑不变
- `nodes/dual_agent.py` 核心流程 - 迭代循环不变
- `agents/evaluator.py` - 评估逻辑不变

---

## 3. 实施路线图

### Phase 1: 基础设施准备 (P0)

**目标**: 建立测试框架，准备新数据类

| 任务 | 负责人 | 依赖 | 验收标准 |
|------|--------|------|----------|
| 创建测试目录结构 | Dev | - | `tests/nodes/`, `tests/agents/` 存在 |
| 编写 NodeTaskConfig 测试 | Dev | - | 测试通过 |
| 编写 Persona 扩展测试 | Dev | - | 测试通过 |
| 编写废弃函数检测测试 | Dev | - | 测试通过 |
| 编写 _bmad 扫描测试 | Dev | - | 测试通过 |

**预计时间**: 1-2 天

### Phase 2: 配置加载重构 (P0)

**目标**: 完成 TDD-BMM-01

```python
# 实施顺序 (严格按此顺序)
1. 添加 NodeTaskConfig 数据类
2. 扩展 NodeDeliverableConfig
3. 重构 NodeConfig (移除废弃字段)
4. 更新 NodeLoader._build_node_config()
5. 重写所有 node.yaml 文件
6. 运行测试确保通过
```

| 任务 | 文件 | 行数预估 |
|------|------|---------|
| 添加 NodeTaskConfig | `loader.py` | +15 |
| 扩展 NodeDeliverableConfig | `loader.py` | +5 |
| 重构 NodeConfig | `loader.py` | -10, +5 |
| 更新加载逻辑 | `loader.py` | +30 |
| 重写 node.yaml (5个) | `nodes/*/` | ~150 行/文件 |

**预计时间**: 2-3 天

### Phase 3: Persona 重构 (P0)

**目标**: 完成 TDD-BMM-02

```python
# 实施顺序
1. 扩展 Persona 数据类 (communication_style)
2. 重写 System Prompt 构建方法
3. 创建5个 BMM persona.json
4. 运行测试确保通过
```

| 任务 | 文件 | 关键变更 |
|------|------|---------|
| 扩展 Persona | `persona.py` | +communication_style |
| 重构 _format_system_prompt | `independent.py` | 完全重写 |
| 创建 analyst persona.json | `nodes/analyst/` | BMM内容 |
| 创建 pm persona.json | `nodes/pm/` | BMM内容 |
| 创建 ux persona.json | `nodes/ux/` | BMM内容 |
| 创建 architect persona.json | `nodes/architect/` | BMM内容 |
| 创建 po persona.json | `nodes/po/` | BMM内容 |

**预计时间**: 2-3 天

### Phase 4: 废弃代码移除 (P0)

**目标**: 完成 TDD-BMM-03

```python
# 实施顺序 (必须按此顺序)
1. 移除 loader.py 废弃数据类
2. 移除 graph.py 废弃函数
3. 移除 dual_agent.py 冗余函数
4. 删除 templates/ 目录
5. 更新 node.yaml 移除废弃字段
6. 运行验证脚本
```

| 任务 | 风险 | 缓解措施 |
|------|------|----------|
| 移除 loader.py 数据类 | 中 | 确保无消费者后再移除 |
| 移除 graph.py 函数 | 低 | 已标记废弃，无活跃使用 |
| 移除 dual_agent.py 函数 | 中 | 确认无外部调用 |
| 删除 templates/ 目录 | 低 | 确认无代码引用 |

**预计时间**: 1-2 天

### Phase 5: 集成测试 (P0)

**目标**: 完成 TDD-BMM-04

| 测试类型 | 覆盖范围 | 目标 |
|----------|---------|------|
| 单元测试 | 单个函数/类 | >90% 覆盖率 |
| 集成测试 | 模块间交互 | 关键路径覆盖 |
| 端到端测试 | 完整流程 | 至少一个节点 |

**预计时间**: 2-3 天

---

## 4. 依赖关系图

```
Phase 1: 基础设施
       │
       ▼
Phase 2: 配置加载重构 ─────────┐
       │                        │
       ▼                        │
Phase 3: Persona 重构 ──────────┤
       │                        │
       ▼                        ▼
Phase 4: 废弃代码移除 ←────── 依赖：Phase 2 完成
       │
       ▼
Phase 5: 集成测试 ←────────── 依赖：Phase 2,3,4 完成
```

**关键依赖**:
- Phase 4 依赖 Phase 2 (NodeConfig 结构稳定后才能移除废弃字段)
- Phase 5 依赖所有前置 Phase

---

## 5. 配置文件模板

### 5.1 node.yaml 模板

```yaml
node_id: {node_id}
name: {display_name}
sequence: {sequence_number}

agent:
  type: independent
  model: sonnet
  temperature: {temp}

task:
  name: {task_name}
  description: >
    {task_description}
  role_supplement: >
    {role_supplement}

deliverable:
  type: {deliverable_type}
  template_title: "{template_title}"
  required_sections:
    - {section_1}
    - {section_2}
    - {section_n}
  output_filename: "{filename_pattern}"
```

### 5.2 persona.json 模板

```json
{
  "name": "{persona_name}",
  "role": "{professional_role}",
  "identity": "{rich_identity_description}",
  "communication_style": "{unique_communication_style}",
  "expertise": [
    "{expertise_area_1}",
    "{expertise_area_2}",
    "{expertise_area_n}"
  ],
  "principles": [
    "{principle_1}",
    "{principle_2}",
    "{principle_n}"
  ],
  "output_format": {
    "type": "{deliverable_type}",
    "format": "markdown"
  }
}
```

---

## 6. 迁移脚本

### 6.1 配置文件迁移脚本

```python
#!/usr/bin/env python3
"""Migrate node configuration from old format to BMM-aligned format."""

import json
import yaml
from pathlib import Path
from typing import Any


# BMM 内容映射 (预处理从 _bmad/bmm/ 提取)
BMM_CONTENT = {
    "analyst": {
        "task": {
            "name": "create-product-brief",
            "description": "Create comprehensive product briefs...",
            "role_supplement": "You are a product-focused Business Analyst..."
        },
        "deliverable": {
            "type": "product-brief",
            "template_title": "Product Brief: {project_name}",
            "required_sections": [
                "executive_summary", "core_vision", "problem_statement",
                "proposed_solution", "key_differentiators", "target_users",
                "success_metrics", "mvp_scope"
            ],
            "output_filename": "product-brief-{project_name}.md"
        },
        "persona": {
            "name": "Mary",
            "role": "Strategic Business Analyst + Requirements Expert",
            "identity": "Senior analyst with deep expertise...",
            "communication_style": "Speaks with the excitement of a treasure hunter...",
            "expertise": ["Market research...", "SWOT analysis..."],
            "principles": ["Ground findings in evidence..."]
        }
    },
    # ... 其他节点
}


def migrate_node_yaml(node_id: str, old_yaml: dict) -> dict:
    """Migrate old node.yaml to new format."""
    bmm = BMM_CONTENT.get(node_id, {})
    
    return {
        "node_id": old_yaml.get("node_id", node_id),
        "name": old_yaml.get("name", node_id),
        "sequence": old_yaml.get("sequence", 0),
        "agent": old_yaml.get("agent", {"type": "independent", "model": "sonnet"}),
        "task": bmm.get("task"),
        "deliverable": {
            **bmm.get("deliverable", {}),
            "type": bmm.get("deliverable", {}).get("type", old_yaml.get("deliverable", {}).get("type", "document"))
        }
        # 注意: 不包含 description, questions, dependencies
    }


def migrate_persona_json(node_id: str) -> dict:
    """Create BMM-aligned persona.json."""
    return BMM_CONTENT.get(node_id, {}).get("persona", {})


def main():
    """Run migration for all nodes."""
    nodes_dir = Path("autoBMAD/nodes")
    
    for node_id in ["analyst", "pm", "ux", "architect", "po"]:
        node_dir = nodes_dir / node_id
        if not node_dir.exists():
            continue
        
        # Migrate node.yaml
        yaml_path = node_dir / "node.yaml"
        if yaml_path.exists():
            with open(yaml_path) as f:
                old_yaml = yaml.safe_load(f)
            
            new_yaml = migrate_node_yaml(node_id, old_yaml)
            
            # Backup old file
            yaml_path.rename(yaml_path.with_suffix(".yaml.bak"))
            
            # Write new file
            with open(yaml_path, 'w') as f:
                yaml.dump(new_yaml, f, default_flow_style=False, sort_keys=False)
            
            print(f"✅ Migrated {node_id}/node.yaml")
        
        # Create new persona.json
        persona = migrate_persona_json(node_id)
        if persona:
            persona_path = node_dir / "persona.json"
            
            # Backup old file
            if persona_path.exists():
                persona_path.rename(persona_path.with_suffix(".json.bak"))
            
            # Write new file
            with open(persona_path, 'w') as f:
                json.dump(persona, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Created {node_id}/persona.json")


if __name__ == "__main__":
    main()
```

---

## 7. 验收标准

### 7.1 功能验收

| 检查项 | 通过标准 |
|--------|----------|
| NodeLoader 加载新格式 | 能正确加载带 task 块的 node.yaml |
| NodeLoader 向后兼容 | 能加载旧格式而不报错 |
| Persona 加载 | 能正确加载含 communication_style 的 persona.json |
| System Prompt 构建 | Prompt 包含所有 BMM 部分 |
| 双代理执行 | Independent + Evaluator 循环正常工作 |
| 交付物保存 | 双层保存机制正常工作 |

### 7.2 代码质量验收

| 检查项 | 通过标准 |
|--------|----------|
| 类型检查 | `basedpyright` 无错误 |
| 代码风格 | `ruff check` 无错误 |
| 测试覆盖率 | 新增代码 >90% |
| 废弃代码 | `_bmad` 引用数为 0 |
| 代码复杂度 | 无新增复杂函数 |

### 7.3 性能验收

| 检查项 | 通过标准 |
|--------|----------|
| 配置加载 | < 10ms |
| Prompt 构建 | < 5ms |
| 节点执行 | 总时间 < 3分钟 (3迭代) |

---

## 8. 回滚策略

### 8.1 分阶段回滚

```
如果 Phase 5 测试失败:
  └─ 回滚 Phase 4 (恢复废弃代码)
  
如果 Phase 4 导致问题:
  └─ 回滚 Phase 3 (恢复旧 persona)
  
如果 Phase 3 导致问题:
  └─ 回滚 Phase 2 (恢复旧 node.yaml 结构)
```

### 8.2 回滚命令

```bash
# 使用 git 回滚到特定阶段
git reset --hard HEAD~N  # N = 需要回滚的提交数

# 或者使用备份文件
mv autoBMAD/nodes/analyst/node.yaml.bak autoBMAD/nodes/analyst/node.yaml
mv autoBMAD/nodes/analyst/persona.json.bak autoBMAD/nodes/analyst/persona.json
```

---

## 9. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 配置文件格式不兼容 | 中 | 高 | 保持向后兼容，task 字段可选 |
| BMM 内容提取不完整 | 低 | 中 | 对照 _bmad/bmm/ 源文件检查 |
| 测试覆盖不足 | 中 | 中 | 强制要求每个功能有测试 |
| 性能退化 | 低 | 低 | 基准测试，监控执行时间 |
| 外部依赖未完全移除 | 中 | 高 | 扫描脚本验证 |

---

## 10. 验证清单

### 实施前检查

- [ ] 所有研究文档已阅读
- [ ] 备份已创建
- [ ] 测试框架准备就绪
- [ ] 团队成员了解实施计划

### 实施后检查

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 类型检查无错误
- [ ] 代码风格检查无错误
- [ ] `_bmad` 引用扫描返回空
- [ ] 端到端测试通过 (至少一个节点)
- [ ] 文档已更新

---

## 11. 参考文档

| 文档 | 位置 | 用途 |
|------|------|------|
| TDD-BMM-01 | `TDD-BMM-01-NodeLoader-Config-Refactor.md` | 配置加载重构 |
| TDD-BMM-02 | `TDD-BMM-02-Persona-SystemPrompt-Refactor.md` | Persona重构 |
| TDD-BMM-03 | `TDD-BMM-03-Deprecated-Code-Removal.md` | 废弃代码移除 |
| TDD-BMM-04 | `TDD-BMM-04-DualAgent-Integration-E2E.md` | 集成测试 |
| Part 1-5 | `docs/research/` | 研究报告 |

---

**文档结束**
