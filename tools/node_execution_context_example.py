"""
NodeExecutionContext 使用示例 - 验证方案B设计

本示例演示如何使用新的 NodeExecutionContext 协议，
展示与旧代码的对比以及改进点。
"""

from typing import Any


def example_old_flow():
    """
    旧流程示例 - 存在问题:
    1. executor 从 state 猜测 task
    2. DualAgentNode 二次包装
    3. IndependentAgent 反向解析
    """
    print("=== 旧流程示例 ===")
    print()
    
    # 1. executor: 从 state 猜测 task
    state = {
        "context_file": '{"subject_context": {"content": "Build a chat app"}}',
        "chained_context": {
            "analyst": {"deliverable": {"title": "Analysis", "content": "..."}}
        }
    }
    
    # 旧代码: _extract_task_from_state
    import json
    context_file = state.get("context_file", "")
    context_data = json.loads(context_file)
    task = context_data.get("subject_context", {}).get("content", "")
    subject_context = "Build a chat app"
    
    print(f"1. executor 猜测 task: {task[:30]}...")
    print()
    
    # 2. DualAgentNode: 二次包装
    # 旧代码: subject_context={"subject": subject_context, "task": task}
    wrapped_context = {"subject": subject_context, "task": task}
    print(f"2. DualAgentNode 二次包装: {wrapped_context}")
    print()
    
    # 3. IndependentAgent: 反向解析
    # 旧代码: 尝试多种路径解析
    subject_context_raw = wrapped_context
    content = None
    
    # 尝试 nested path
    nested_ctx = subject_context_raw.get("subject_context", {})
    if isinstance(nested_ctx, dict):
        content = nested_ctx.get("content")
    
    # 尝试 flat path
    if not content:
        content = subject_context_raw.get("content")
    
    print(f"3. IndependentAgent 反向解析: {content[:30] if content else 'N/A'}...")
    print()
    
    print("X 问题: 多层猜测和包装，容易出错")
    print()


def example_new_flow():
    """
    新流程示例 - 使用 NodeExecutionContext:
    1. executor 构建明确的执行上下文
    2. DualAgentNode 直接传递
    3. IndependentAgent 直接使用
    """
    print("=== 新流程示例 (方案B) ===")
    print()
    
    # 0. node.yaml 配置 (来源)
    node_config = {
        "node_id": "pm",
        "name": "Product Manager",
        "description": "Create a comprehensive PRD",
        "deliverable_type": "prd",
        "deliverable": {
            "required_sections": [
                "Overview",
                "User Stories", 
                "Acceptance Criteria"
            ]
        }
    }
    
    # 1. executor: 构建明确的 NodeExecutionContext
    from tools.node_execution_context_researcher import NodeExecutionContextResearcher
    
    execution_context = {
        # 身份标识
        "pipeline_id": "pipeline-123",
        "node_id": "pm",
        "node_name": "Product Manager",
        "node_order": 2,
        
        # 任务契约 - 直接来自 node.yaml
        "task_name": node_config["name"],
        "task_description": node_config["description"],
        "role_supplement": "",  # 旧 schema 默认值
        
        # 交付物契约
        "deliverable_type": node_config["deliverable_type"],
        "deliverable_requirements": {
            "required_sections": node_config["deliverable"]["required_sections"],
            "template_title": "PRD"
        },
        
        # 上下文数据
        "original_context": {"content": "Build a chat app"},
        "chained_deliverables": [
            {"node_id": "analyst", "title": "Analysis", "summary": "..."}
        ],
        "shared_context": {},
        
        # 迭代状态
        "iteration_feedback": None,
        
        # 扩展上下文
        "docs_context": []
    }
    
    print("1. executor 构建 NodeExecutionContext:")
    print(f"   - task_name: {execution_context['task_name']}")
    print(f"   - task_description: {execution_context['task_description'][:40]}...")
    print(f"   - required_sections: {execution_context['deliverable_requirements']['required_sections']}")
    print()
    
    # 2. DualAgentNode: 直接传递 execution_context
    print("2. DualAgentNode 直接传递 execution_context (无包装)")
    print("   await node.execute_with_context(execution_context)")
    print()
    
    # 3. ContextManager: 裁剪为 IndependentAgentInput
    independent_input = {
        "task_name": execution_context["task_name"],
        "task_description": execution_context["task_description"],
        "role_supplement": execution_context["role_supplement"],
        "deliverable_requirements": execution_context["deliverable_requirements"],
        "original_context_summary": execution_context["original_context"]["content"],
        "chained_deliverables_summary": [
            {"node_id": d["node_id"], "title": d["title"], "summary": d["summary"][:50]}
            for d in execution_context["chained_deliverables"]
        ],
        "iteration_feedback": None,
        "persona_context": {}
    }
    
    print("3. ContextManager 裁剪为 IndependentAgentInput:")
    print(f"   - task_name: {independent_input['task_name']}")
    print(f"   - original_context: {independent_input['original_context_summary']}")
    print()
    
    # 4. IndependentAgent: 直接使用字段
    print("4. IndependentAgent 直接使用字段:")
    print(f"   task_name = agent_input['task_name']  # 直接读取")
    print(f"   # 无需 json.loads, 无需猜测路径")
    print()
    
    # 展示构建的 prompt
    prompt_sections = [
        f"## 任务: {independent_input['task_name']}",
        f"{independent_input['task_description']}",
        "",
        "## 交付物要求",
        "必须包含以下章节:",
    ]
    for section in independent_input['deliverable_requirements']['required_sections']:
        prompt_sections.append(f"- {section}")
    
    prompt = "\n".join(prompt_sections)
    
    print("5. 生成的 Prompt (包含节点契约):")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    print("V 优势:")
    print("   - 无猜测逻辑")
    print("   - 无二次包装")
    print("   - 节点契约明确进入 prompt")
    print("   - 五个节点的 prompt 差异来自 node.yaml")


def example_comparison():
    """对比展示"""
    print()
    print("=" * 60)
    print("新旧方案对比")
    print("=" * 60)
    print()
    
    comparison = """
┌─────────────────┬────────────────────────┬────────────────────────┐
│     阶段        │         旧方案          │         新方案 (B)      │
├─────────────────┼────────────────────────┼────────────────────────┤
│ executor        │ _extract_task_from_    │ NodeExecutionContext   │
│                 │   state() - 猜测       │   Builder - 明确构建    │
├─────────────────┼────────────────────────┼────────────────────────┤
│ DualAgentNode   │ {subject, task} 包装   │ 直接传递 execution_ctx │
├─────────────────┼────────────────────────┼────────────────────────┤
│ ContextManager  │ build_independent_     │ build_independent_     │
│                 │   context() - 原始     │   input() - 裁剪       │
├─────────────────┼────────────────────────┼────────────────────────┤
│ IndependentAgent│ 反向解析 nested/flat   │ 直接读取 agent_input   │
│                 │   多种路径             │   字段                 │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Prompt 内容     │ 只有 persona + task    │ persona + 节点契约     │
│                 │   文本                 │   (name/description/   │
│                 │                        │   required_sections)   │
├─────────────────┼────────────────────────┼────────────────────────┤
│ 节点差异来源    │ 只有 persona 不同      │ persona + 任务契约     │
│                 │                        │   + 交付物要求         │
└─────────────────┴────────────────────────┴────────────────────────┘
    """
    print(comparison)


def example_node_contract_in_prompt():
    """展示节点契约如何进入 prompt"""
    print()
    print("=" * 60)
    print("节点契约进入 Prompt 示例")
    print("=" * 60)
    print()
    
    # 五个节点的不同契约
    nodes = [
        {
            "node_id": "analyst",
            "name": "Requirements Analyst",
            "description": "Analyze requirements and create specification",
            "required_sections": ["Problem Statement", "User Personas", "Functional Requirements"]
        },
        {
            "node_id": "pm",
            "name": "Product Manager",
            "description": "Create comprehensive Product Requirements Document",
            "required_sections": ["Overview", "User Stories", "Acceptance Criteria"]
        },
        {
            "node_id": "ux",
            "name": "UX Designer",
            "description": "Design user experience and interface",
            "required_sections": ["User Flows", "Wireframes", "Interaction Design"]
        },
        {
            "node_id": "architect",
            "name": "System Architect",
            "description": "Design system architecture and technical specification",
            "required_sections": ["Architecture Overview", "Component Design", "API Specification"]
        },
        {
            "node_id": "po",
            "name": "Product Owner",
            "description": "Create epics and user stories for implementation",
            "required_sections": ["Epics", "User Stories", "Implementation Notes"]
        }
    ]
    
    for node in nodes:
        print(f"--- {node['name']} ({node['node_id']}) ---")
        print(f"任务描述: {node['description']}")
        print(f"必选章节: {', '.join(node['required_sections'])}")
        print()
    
    print("V 结果: 每个节点的 prompt 都包含其特定的任务契约")
    print("   而不仅仅是 persona 的差异")


def main():
    """运行所有示例"""
    example_old_flow()
    print()
    input("按 Enter 继续...")
    print()
    
    example_new_flow()
    print()
    input("按 Enter 继续...")
    print()
    
    example_comparison()
    print()
    input("按 Enter 继续...")
    print()
    
    example_node_contract_in_prompt()


if __name__ == "__main__":
    main()
