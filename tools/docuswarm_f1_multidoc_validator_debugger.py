"""
F1: [ICON]

[ICON]

[ICON]
- IndependentAgent [ICON] submit_execution_report [ICON] multi-document [ICON]
- [ICON] IndependentOutputValidationStrategy._validate_deliverable() [ICON] file_path [ICON] sha256
- MaxDeliverablesValidationStrategy [ICON] document_total [ICON] deliverable.documents[]

[ICON]:
    python tools/docuswarm_f1_multidoc_validator_debugger.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from autoBMAD.docuswarm.context.validator import (
    ContextValidator,
    IndependentOutputValidationStrategy,
    MaxDeliverablesValidationStrategy,
)


def test_multi_document_validation():
    """[ICON]."""
    print("=" * 80)
    print("F1 [ICON]")
    print("=" * 80)
    
    # [ICON] IndependentAgent._parse_response [ICON]
    multi_doc_data = {
        "deliverable": {
            "title": "PO Deliverables Set",
            "type": "multi-document",
            "documents": [
                {
                    "title": "Product Vision",
                    "file_path": "output/pipe-123/po/product-vision.md",
                    "sha256": "abc123...",
                    "content_summary": "Product vision summary...",
                    "word_count": 500,
                    "document_type": "product-vision",
                    "document_index": 1,
                    "document_total": 4,
                },
                {
                    "title": "Roadmap",
                    "file_path": "output/pipe-123/po/roadmap.md",
                    "sha256": "def456...",
                    "content_summary": "Roadmap summary...",
                    "word_count": 800,
                    "document_type": "roadmap",
                    "document_index": 2,
                    "document_total": 4,
                },
                {
                    "title": "Epic List",
                    "file_path": "output/pipe-123/po/epic-list.md",
                    "sha256": "ghi789...",
                    "content_summary": "Epic list summary...",
                    "word_count": 1200,
                    "document_type": "epic-list",
                    "document_index": 3,
                    "document_total": 4,
                },
                {
                    "title": "Story List",
                    "file_path": "output/pipe-123/po/story-list.md",
                    "sha256": "jkl012...",
                    "content_summary": "Story list summary...",
                    "word_count": 1500,
                    "document_type": "story-list",
                    "document_index": 4,
                    "document_total": 4,
                },
            ],
            "total_word_count": 4000,
        },
        "questions": [],
        "action": "create_deliverable",
    }
    
    print("\n[TEST DATA] [ICON]:")
    print(json.dumps(multi_doc_data, indent=2, ensure_ascii=False))
    
    # [ICON] ContextValidator.validate_independent_output
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 1: ContextValidator.validate_independent_output()")
    print("-" * 60)
    
    validator = ContextValidator()
    result = validator.validate_independent_output(multi_doc_data, node_id="po")
    
    print(f"\n[ICON]: valid={result.valid}")
    if result.issues:
        print(f"[ICON] {len(result.issues)} [ICON]:")
        for issue in result.issues:
            print(f"  - [{issue.code}] {issue.field}: {issue.message}")
    else:
        print("[ICON]")
    
    # [ICON] MaxDeliverablesValidationStrategy
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 2: MaxDeliverablesValidationStrategy")
    print("-" * 60)
    
    max_deliv_strategy = MaxDeliverablesValidationStrategy()
    max_result = max_deliv_strategy.validate(
        multi_doc_data,
        config={"max_deliverables": 5, "node_id": "po"}
    )
    
    print(f"\n[ICON]: valid={max_result.valid}")
    print(f"[ICON]: {max_deliv_strategy._detect_document_count(multi_doc_data['deliverable'])}")
    if max_result.issues:
        print(f"[ICON] {len(max_result.issues)} [ICON]:")
        for issue in max_result.issues:
            print(f"  - [{issue.code}] {issue.field}: {issue.message}")
    
    # [ICON]
    print("\n" + "-" * 60)
    print("[ICON] [ICON] 3: [ICON]")
    print("-" * 60)
    
    single_doc_data = {
        "deliverable": {
            "title": "Single Document",
            "file_path": "output/pipe-123/pm/product-requirements.md",
            "sha256": "xyz789...",
            "content_summary": "Single doc summary...",
        },
        "questions": [],
        "action": "create_deliverable",
    }
    
    single_result = validator.validate_independent_output(single_doc_data, node_id="pm")
    print(f"\n[ICON]: valid={single_result.valid}")
    if single_result.issues:
        for issue in single_result.issues:
            print(f"  - [{issue.code}] {issue.field}: {issue.message}")
    else:
        print("[ICON] [ICON]")
    
    return {
        "multi_doc_valid": result.valid,
        "multi_doc_issues": len(result.issues),
        "single_doc_valid": single_result.valid,
        "detected_doc_count": max_deliv_strategy._detect_document_count(multi_doc_data["deliverable"]),
    }


def analyze_validator_code():
    """[ICON]."""
    print("\n" + "=" * 80)
    print("F1 [ICON]")
    print("=" * 80)
    
    print("""
[ICON]:

1. IndependentAgent._parse_response() (autoBMAD/docuswarm/agents/independent.py:622-636)
   - [ICON] multi-document [ICON] deliverable
   - [ICON]: {type: "multi-document", documents: [...], total_word_count: ...}
   - [ICON]: [ICON] file_path [ICON] sha256

2. IndependentOutputValidationStrategy._validate_deliverable() (validator.py:668-756)
   - [ICON] file_path [ICON] ([ICON] 719-736)
   - [ICON] sha256 [ICON] ([ICON] 739-756)
   - [ICON] multi-document [ICON]

3. MaxDeliverablesValidationStrategy._detect_document_count() (validator.py:1288-1306)
   - [ICON] document_total [ICON]
   - [ICON] documents [ICON]
   - [ICON] document_total [ICON] 1[ICON]

[ICON]:

A. [ICON] _validate_deliverable() [ICON] multi-document [ICON]:
   ```python
   if deliverable.get("type") == "multi-document":
       # [ICON] documents [ICON]
       documents = deliverable.get("documents", [])
       for i, doc in enumerate(documents):
           # [ICON] file_path [ICON] sha256
   else:
       # [ICON]
   ```

B. [ICON] _detect_document_count() [ICON] documents [ICON]:
   ```python
   if deliverable.get("type") == "multi-document":
       documents = deliverable.get("documents", [])
       return len(documents)
   # [ICON] document_total [ICON]
   ```

C. [ICON] document_total [ICON]:
   - IndependentAgent [ICON] multi-document [ICON] document_total
   - [ICON] document_index [ICON] document_total
""")


def main():
    """[ICON]."""
    print("\n[DEBUG] DocuSwarm F1 [ICON]\n")
    
    results = test_multi_document_validation()
    analyze_validator_code()
    
    # [ICON]
    print("\n" + "=" * 80)
    print("F1 [ICON]")
    print("=" * 80)
    print(f"""
[ICON]:
- [ICON]: {'[ICON] [ICON]' if results['multi_doc_valid'] else '[ICON] [ICON]'}
- [ICON]: {results['multi_doc_issues']}
- [ICON]: {results['detected_doc_count']} ([ICON]: 4)
- [ICON]: {'[ICON] [ICON]' if results['single_doc_valid'] else '[ICON] [ICON]'}

[ICON]:
[WARNING] [ICON] - validator [ICON] multi-document [ICON]
if not results['multi_doc_valid'] else 
[ICON] [ICON]

[ICON]:
- architect / po [ICON]
- 03-document-creation-constraints.md [ICON]
- [ICON] NodeResult.documents[ICON]create_deliverable [ICON]
  submit_execution_report [ICON] schema [ICON]
  [ICON]
""")
    
    return 0 if results['multi_doc_valid'] else 1


if __name__ == "__main__":
    sys.exit(main())
