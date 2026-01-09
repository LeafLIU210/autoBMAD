"""Debug test to check module imports."""



def test_debug_imports():
    """Debug test to check each import."""
    print("\n=== Testing imports ===")

    try:
        print("Importing PromptSystem...")
        from spec_automation.prompts import PromptSystem
        print(f"✓ PromptSystem: {PromptSystem}")
        p = PromptSystem()
        print(f"✓ PromptSystem created: {p}")
    except Exception as e:
        print(f"✗ PromptSystem failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\nImporting TDDWorkflowEngine...")
        from spec_automation.tdd_workflow import TDDWorkflowEngine
        print(f"✓ TDDWorkflowEngine: {TDDWorkflowEngine}")
    except Exception as e:
        print(f"✗ TDDWorkflowEngine failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\nImporting TestVerifier...")
        from spec_automation.test_verifier import TestVerifier
        print(f"✓ TestVerifier: {TestVerifier}")
        tv = TestVerifier()
        print(f"✓ TestVerifier created: {tv}")
    except Exception as e:
        print(f"✗ TestVerifier failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\nImporting QualityGateRunner...")
        from spec_automation.quality_gates import QualityGateRunner
        print(f"✓ QualityGateRunner: {QualityGateRunner}")
        qgr = QualityGateRunner()
        print(f"✓ QualityGateRunner created: {qgr}")
    except Exception as e:
        print(f"✗ QualityGateRunner failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\nImporting SpecStateManager...")
        from spec_automation.spec_state_manager import SpecStateManager
        from pathlib import Path
        print(f"✓ SpecStateManager: {SpecStateManager}")
        ssm = SpecStateManager(db_path=Path("test.db"))
        print(f"✓ SpecStateManager created: {ssm}")
    except Exception as e:
        print(f"✗ SpecStateManager failed: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("\nImporting DocumentParser...")
        from spec_automation.doc_parser import DocumentParser
        print(f"✓ DocumentParser: {DocumentParser}")
        dp = DocumentParser()
        print(f"✓ DocumentParser created: {dp}")
    except Exception as e:
        print(f"✗ DocumentParser failed: {e}")
        import traceback
        traceback.print_exc()
