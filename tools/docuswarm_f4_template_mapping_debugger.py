"""
F4: [ICON]

[ICON]

[ICON]
- TemplateLoader.DEFAULT_TEMPLATES_DIR [ICON] docuswarm/templates
- ContractBuilder [ICON] key [ICON]template_title [ICON] deliverable_type
- ContextManager [ICON] template_title [ICON] node_config.deliverable_type
- [ICON] ID [ICON]

[ICON]:
    python tools/docuswarm_f4_template_mapping_debugger.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.docuswarm.prompts.contract_builder import NodePromptContractBuilder as ContractBuilder
from autoBMAD.docuswarm.prompts.template_loader import TemplateLoader


TEMPLATES_DIR = project_root / "autoBMAD" / "docuswarm" / "templates"
NODES_DIR = project_root / "autoBMAD" / "nodes"


def load_all_templates():
    """[ICON]."""
    templates = {}
    
    for template_file in TEMPLATES_DIR.glob("*_templates.yaml"):
        node_id = template_file.name.replace("_templates.yaml", "")
        with open(template_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        templates[node_id] = data
    
    return templates


def load_all_node_configs():
    """[ICON]."""
    configs = {}
    
    for node_dir in NODES_DIR.iterdir():
        if node_dir.is_dir():
            node_yaml = node_dir / "node.yaml"
            if node_yaml.exists():
                with open(node_yaml, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                configs[data.get("node_id", node_dir.name)] = data
    
    return configs


def analyze_template_mapping():
    """[ICON]."""
    print("=" * 80)
    print("F4 [ICON]")
    print("=" * 80)
    
    templates = load_all_templates()
    configs = load_all_node_configs()
    
    print("\n[ICON] [ICON]:")
    for node_id in sorted(templates.keys()):
        template_data = templates[node_id]
        template_list = template_data.get("templates", [])
        print(f"  - {node_id}_templates.yaml: {len(template_list)} [ICON]")
        for t in template_list:
            print(f"    - {t.get('template_id')}: {t.get('title')}")
    
    print("\n[ICON] [ICON]:")
    for node_id in sorted(configs.keys()):
        config = configs[node_id]
        deliverable_type = config.get("deliverable_type", "N/A")
        print(f"  - {node_id}: deliverable_type='{deliverable_type}'")
    
    # [ICON]
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    builder = ContractBuilder()
    
    mapping_results = []
    for node_id in sorted(configs.keys()):
        config = configs[node_id]
        deliverable_type = config.get("deliverable_type", "")
        
        # [ICON] ContractBuilder._load_node_template [ICON]
        template_data = builder._load_node_template(node_id, deliverable_type)
        
        matched = template_data is not None
        mapping_results.append({
            "node_id": node_id,
            "lookup_key": deliverable_type,
            "matched": matched,
            "template_id": template_data.get("template_id") if matched else None,
        })
        
        status = "[OK] [ICON]" if matched else "[FAIL] [ICON]"
        print(f"  {node_id}: lookup='{deliverable_type}' -> {status}")
        if matched:
            print(f"    [ICON]: {template_data.get('template_id')}")
    
    # [ICON]
    matched_count = sum(1 for r in mapping_results if r["matched"])
    total_count = len(mapping_results)
    match_rate = matched_count / total_count * 100 if total_count > 0 else 0
    
    print(f"\n[ICON]: {matched_count}/{total_count} ({match_rate:.1f}%)")
    
    # [ICON]
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    po_templates = templates.get("po", {})
    po_template_list = po_templates.get("templates", [])
    
    print(f"\nPO [ICON]: {len(po_template_list)}")
    
    # [ICON]
    has_multi_doc_metadata = False
    for t in po_template_list:
        sections = t.get("sections", [])
        for section in sections:
            if any(k in section for k in ["document_index", "document_total", "required_sections"]):
                has_multi_doc_metadata = True
                break
    
    print(f"[ICON]: {'[ICON] [ICON]' if has_multi_doc_metadata else '[ICON] [ICON]'}")
    
    # [ICON] deliverable.document_types [ICON]
    po_config = configs.get("po", {})
    deliverable_config = po_config.get("deliverable", {})
    document_types = deliverable_config.get("document_types", [])
    print(f"PO [ICON] document_types: {document_types}")
    
    return {
        "templates": templates,
        "configs": configs,
        "mapping_results": mapping_results,
        "match_rate": match_rate,
        "has_multi_doc_metadata": has_multi_doc_metadata,
        "document_types": document_types,
    }


def analyze_template_loader_usage():
    """[ICON] TemplateLoader [ICON]."""
    print("\n" + "=" * 80)
    print("F4 TemplateLoader [ICON]")
    print("=" * 80)
    
    print("""
[ICON]:

1. ContractBuilder._build_deliverable_section() (contract_builder.py:212-261)
   - [ICON] context [ICON] deliverable_requirements
   - [ICON] template_title ([ICON] deliverable_type)
   - [ICON] _load_node_template(node_id, template_title)

2. ContractBuilder._load_node_template() (contract_builder.py:263-316)
   - [ICON] templates/{node_id}_templates.yaml
   - [ICON] template_id [ICON]
   - [ICON] title [ICON]

3. TemplateLoader.load_template() (template_loader.py:103-154)
   - [ICON]
   - [ICON]
   - [ICON]

[ICON]:

A. [ICON] key [ICON]
   - [ICON] deliverable_type: "product-brief"
   - [ICON] template_id: "prd"
   - [ICON]

B. [ICON]
   - po_templates.yaml [ICON]
   - [ICON] document_type [ICON]
   - [ICON] product-vision, roadmap, epic-list, story-list [ICON]

C. TemplateLoader vs ContractBuilder [ICON]
   - TemplateLoader [ICON] (e.g., "pm_templates")
   - ContractBuilder [ICON] node_id + template_id [ICON]
   - [ICON]

[ICON]:

[ICON] A: [ICON] ID
   1. [ICON] deliverable_type [ICON] template_id
   2. [ICON] template_id [ICON]

[ICON] B: [ICON]
   1. [ICON] template_mapping:
      ```yaml
      deliverable:
        template_mapping:
          product-vision: product_vision_template
          roadmap: roadmap_template
          epic-list: epic_list_template
      ```
   2. ContractBuilder [ICON] document_type [ICON]

[ICON] C: [ICON]
   1. [ICON] document_type [ICON] ID
   2. [ICON]: "epic-list" -> [ICON] "epic_list" [ICON]
   3. [ICON]
""")


def check_template_structure():
    """[ICON]."""
    print("\n" + "-" * 60)
    print("[ICON] [ICON]")
    print("-" * 60)
    
    templates = load_all_templates()
    
    for node_id, template_data in sorted(templates.items()):
        print(f"\n{node_id}_templates.yaml:")
        template_list = template_data.get("templates", [])
        
        for template in template_list:
            template_id = template.get("template_id", "N/A")
            title = template.get("title", "N/A")
            sections = template.get("sections", [])
            
            print(f"  - {template_id}: '{title}'")
            print(f"    sections: {len(sections)} [ICON]")
            
            # [ICON] section [ICON]
            required_sections = [s.get("heading") for s in sections if s.get("required")]
            print(f"    required sections: {required_sections}")


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F4 [ICON]\n")
    
    results = analyze_template_mapping()
    analyze_template_loader_usage()
    check_template_structure()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F4 [ICON]")
    print("=" * 80)
    
    unmapped_nodes = [r["node_id"] for r in results["mapping_results"] if not r["matched"]]
    
    print(f"""
[ICON]:
- [ICON]: {results['match_rate']:.1f}%
- [ICON]: {unmapped_nodes if unmapped_nodes else '[ICON]'}
- [ICON]: {'[ICON] [ICON]' if results['has_multi_doc_metadata'] else '[ICON] [ICON]'}
- PO [ICON] document_types: {results['document_types']}

[ICON]:
{"[ICON] [ICON] - [ICON] ID [ICON]"
if results['match_rate'] < 100 else 
"[ICON] [ICON]"}

[ICON]:
""")
    
    for r in results["mapping_results"]:
        status = "[ICON]" if r["matched"] else "[ICON]"
        print(f"  {status} {r['node_id']}: lookup='{r['lookup_key']}' -> template='{r.get('template_id', 'N/A')}'")
    
    print(f"""
[ICON]:
- [ICON]"[ICON]"[ICON]"[ICON]"
- 03-document-creation-constraints.md [ICON]
- [ICON]
- F8 [ICON]"[ICON]"[ICON]"[ICON]"

[ICON]: MEDIUM
""")
    
    return 0 if results['match_rate'] == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
