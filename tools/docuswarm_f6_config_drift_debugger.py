"""
F6: Analyst [ICON]

[ICON]Analyst [ICON]

[ICON]
- 02-node-configurations-reference.md [ICON] Analyst [ICON]
- [ICON] node.yaml [ICON] required_sections [ICON] questions [ICON]
- [ICON]

[ICON]:
    python tools/docuswarm_f6_config_drift_debugger.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# [ICON] ([ICON] 02-node-configurations-reference.md)
REFERENCE_CONFIG = {
    "node_id": "analyst",
    "task": {
        "name": "conduct-product-discovery",
        "description": "Guide teams to understand product intent through collaborative discovery",
        "skill_ref": "bmad-product-discovery",
    },
    "deliverable": {
        "type": "product-brief",
        "required_sections": [
            "product_overview",
            "market_context",
            "competitive_landscape",
            "value_proposition",
            "target_users",
            "executive_summary",
        ],
    },
    "questions": [
        {"id": "q1", "text": "What is the core product idea or problem you're trying to solve?", "required": True},
        {"id": "q2", "text": "Who are your target users and what do you know about them?", "required": True},
        {"id": "q3", "text": "Do you have any existing materials (docs, sketches, prototypes)?", "required": False},
    ],
}


def load_current_config():
    """[ICON] Analyst [ICON]."""
    analyst_yaml = project_root / "autoBMAD" / "nodes" / "analyst" / "node.yaml"
    
    with open(analyst_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def analyze_config_drift():
    """[ICON]."""
    print("=" * 80)
    print("F6 Analyst [ICON]")
    print("=" * 80)
    
    current = load_current_config()
    reference = REFERENCE_CONFIG
    
    print("\n[ICON] [ICON] (02-node-configurations-reference.md):")
    print(f"  task.name: {reference['task']['name']}")
    print(f"  task.skill_ref: {reference['task']['skill_ref']}")
    print(f"  deliverable.required_sections: {reference['deliverable']['required_sections']}")
    print(f"  questions: {len(reference['questions'])} [ICON]")
    for q in reference['questions']:
        print(f"    - {q['id']}: {q['text'][:50]}...")
    
    print("\n[ICON] [ICON] (analyst/node.yaml):")
    print(f"  task.name: {current['task']['name']}")
    print(f"  task.skill_ref: {current['task']['skill_ref']}")
    print(f"  deliverable.required_sections: {current['deliverable']['required_sections']}")
    print(f"  questions: {len(current['questions'])} [ICON]")
    for q in current['questions']:
        print(f"    - {q['id']}: {q['text'][:50]}...")
    
    # [ICON]
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    differences = []
    
    # [ICON] task.name
    if current['task']['name'] != reference['task']['name']:
        differences.append({
            "field": "task.name",
            "reference": reference['task']['name'],
            "current": current['task']['name'],
            "type": "value_changed",
        })
        print(f"\n[ICON] task.name [ICON]:")
        print(f"  [ICON]: {reference['task']['name']}")
        print(f"  [ICON]: {current['task']['name']}")
    else:
        print(f"\n[ICON] task.name [ICON]: {current['task']['name']}")
    
    # [ICON] skill_ref
    if current['task']['skill_ref'] != reference['task']['skill_ref']:
        differences.append({
            "field": "task.skill_ref",
            "reference": reference['task']['skill_ref'],
            "current": current['task']['skill_ref'],
            "type": "value_changed",
        })
        print(f"\n[ICON] task.skill_ref [ICON]:")
        print(f"  [ICON]: {reference['task']['skill_ref']}")
        print(f"  [ICON]: {current['task']['skill_ref']}")
    else:
        print(f"\n[ICON] task.skill_ref [ICON]: {current['task']['skill_ref']}")
    
    # [ICON] required_sections
    current_sections = set(current['deliverable']['required_sections'])
    reference_sections = set(reference['deliverable']['required_sections'])
    
    only_in_current = current_sections - reference_sections
    only_in_reference = reference_sections - current_sections
    
    if only_in_current or only_in_reference:
        differences.append({
            "field": "deliverable.required_sections",
            "only_in_current": list(only_in_current),
            "only_in_reference": list(only_in_reference),
            "type": "set_different",
        })
        print(f"\n[ICON] deliverable.required_sections [ICON]:")
        if only_in_reference:
            print(f"  [ICON]: {list(only_in_reference)}")
        if only_in_current:
            print(f"  [ICON]: {list(only_in_current)}")
    else:
        print(f"\n[ICON] deliverable.required_sections [ICON]: {list(current_sections)}")
    
    # [ICON] questions
    current_questions = {q['text']: q for q in current['questions']}
    reference_questions = {q['text']: q for q in reference['questions']}
    
    current_q_texts = set(current_questions.keys())
    reference_q_texts = set(reference_questions.keys())
    
    only_in_current_q = current_q_texts - reference_q_texts
    only_in_reference_q = reference_q_texts - current_q_texts
    
    if only_in_current_q or only_in_reference_q:
        differences.append({
            "field": "questions",
            "only_in_current": len(only_in_current_q),
            "only_in_reference": len(only_in_reference_q),
            "type": "set_different",
        })
        print(f"\n[ICON] questions [ICON]:")
        if only_in_reference_q:
            print(f"  [ICON]:")
            for q in only_in_reference_q:
                print(f"    - {q[:60]}...")
        if only_in_current_q:
            print(f"  [ICON]:")
            for q in only_in_current_q:
                print(f"    - {q[:60]}...")
    else:
        print(f"\n[ICON] questions [ICON] ([ICON]: {len(current['questions'])})")
    
    return {
        "differences": differences,
        "difference_count": len(differences),
        "reference": reference,
        "current": current,
    }


def check_reference_document():
    """[ICON]."""
    print("\n" + "=" * 80)
    print("F6 [ICON]")
    print("=" * 80)
    
    reference_doc = project_root / "docs" / "research" / "docuswarm-deep-reform" / "02-node-configurations-reference.md"
    
    if reference_doc.exists():
        print(f"\n[ICON] [ICON]: {reference_doc}")
        
        # [ICON] Analyst [ICON]
        with open(reference_doc, "r", encoding="utf-8") as f:
            content = f.read()
        
        # [ICON] Analyst [ICON]
        if "analyst" in content.lower():
            print("[ICON] [ICON] analyst [ICON]")
        else:
            print("[ICON] [ICON] analyst [ICON]")
        
        # [ICON]
        required_sections = ["product_overview", "market_context", "competitive_landscape"]
        for section in required_sections:
            if section in content:
                print(f"[ICON] [ICON] {section}")
            else:
                print(f"[ICON] [ICON] {section}")
    else:
        print(f"\n[ICON] [ICON]: {reference_doc}")
        print("  [ICON]")


def analyze_drift_impact():
    """[ICON]."""
    print("\n" + "=" * 80)
    print("F6 [ICON]")
    print("=" * 80)
    
    print("""
[ICON]:

[ICON]:
- F7 [ICON]: Analyst [ICON] task.name [ICON] skill_ref [ICON] bmad-product-brief
- [ICON] 02-node-configurations-reference.md [ICON]

[ICON]:

1. Task Name
   - [ICON]: conduct-product-discovery
   - [ICON]: create-product-brief
   - [ICON]: [ICON]

2. Skill Reference
   - [ICON]: bmad-product-discovery
   - [ICON]: bmad-product-brief
   - [ICON]: [ICON] skill [ICON]

3. Required Sections
   - [ICON]: product_overview, market_context, competitive_landscape,
           value_proposition, target_users, executive_summary
   - [ICON]: executive_summary, product_vision, target_users,
           value_proposition, key_features, success_metrics
   - [ICON]: [ICON]

4. Questions
   - [ICON]: [ICON] / [ICON] / [ICON]
   - [ICON]: [ICON] / [ICON] / [ICON]
   - [ICON]: [ICON]

[ICON]:

[ICON] A: [ICON] ([ICON])
   1. 02-node-configurations-reference.md [ICON]
   2. [ICON]
   3. [ICON]

[ICON] B: [ICON]
   1. [ICON]
   2. [ICON] analyst/node.yaml [ICON]
   3. [ICON]

[ICON] C: [ICON]
   1. [ICON]
   2. [ICON]
   3. [ICON]

[ICON]:
F7 [ICON]
[ICON] 02-node-configurations-reference.md [ICON]"[ICON]"[ICON]
[ICON]"[ICON]"[ICON]
""")


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F6 Analyst [ICON]\n")
    
    results = analyze_config_drift()
    check_reference_document()
    analyze_drift_impact()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F6 [ICON]")
    print("=" * 80)
    print(f"""
[ICON]:
- [ICON]: {results['difference_count']}
- [ICON]: {[d['field'] for d in results['differences']]}

[ICON]:
{"[ICON] [ICON] - Analyst [ICON]"
if results['difference_count'] > 0 else 
"[ICON] [ICON]"}

[ICON]:
- [ICON] 02-node-configurations-reference.md [ICON]
  [ICON] Analyst [ICON]
- [ICON]"[ICON] / [ICON]"

[ICON]:
- [ICON] F7 [ICON]
- [ICON]
- [ICON]: LOW ([ICON])

[ICON]:
""")
    
    for d in results['differences']:
        print(f"  - {d['field']}: {d['type']}")
        if d['type'] == 'value_changed':
            print(f"    [ICON]: {d['reference']}")
            print(f"    [ICON]: {d['current']}")
        elif d['type'] == 'set_different':
            if 'only_in_reference' in d:
                print(f"    [ICON]: {d['only_in_reference']}")
            if 'only_in_current' in d:
                print(f"    [ICON]: {d['only_in_current']}")
    
    return 0 if results['difference_count'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
