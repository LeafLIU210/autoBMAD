#!/usr/bin/env python3
"""
Status System Refactor Verification Script
Verifies that the refactored status system works correctly
"""

import sys
import traceback
from pathlib import Path

# Add project path
project_root = Path(__file__).parent / "autoBMAD" / "epic_automation"
sys.path.insert(0, str(project_root))

def test_imports():
    """Test imports of all key modules"""
    print("=" * 60)
    print("Test 1: Import Key Modules")
    print("=" * 60)

    try:
        # Test story_parser
        from story_parser import (
            ProcessingStatus,
            CORE_STATUS_VALUES,
            core_status_to_processing,
            is_core_status_valid,
            _normalize_story_status,
        )
        print("OK: story_parser imported successfully")

        # Test qa_tools_integration
        from qa_tools_integration import ProcessingStatus as QAProcessingStatus
        print("OK: qa_tools_integration imported successfully")

        # Test state_manager
        from state_manager import StateManager
        print("OK: state_manager imported successfully")

        # Test qa_agent
        from qa_agent import QAAgent
        print("OK: qa_agent imported successfully")

        # Test dev_agent
        from dev_agent import DevAgent
        print("OK: dev_agent imported successfully")

        # Test sm_agent
        from sm_agent import SMAgent
        print("OK: sm_agent imported successfully")

        return True
    except Exception as e:
        print(f"ERROR: Import failed: {e}")
        traceback.print_exc()
        return False

def test_processing_status():
    """Test ProcessingStatus enum"""
    print("\n" + "=" * 60)
    print("Test 2: ProcessingStatus Enum")
    print("=" * 60)

    try:
        from story_parser import ProcessingStatus

        # Check if QA states exist
        assert hasattr(ProcessingStatus, 'QA_PASS'), "QA_PASS state does not exist"
        assert hasattr(ProcessingStatus, 'QA_CONCERNS'), "QA_CONCERNS state does not exist"
        assert hasattr(ProcessingStatus, 'QA_FAIL'), "QA_FAIL state does not exist"
        assert hasattr(ProcessingStatus, 'QA_WAIVED'), "QA_WAIVED state does not exist"

        print("OK: QA status enum exists")

        # Check if story states exist
        assert hasattr(ProcessingStatus, 'PENDING'), "PENDING state does not exist"
        assert hasattr(ProcessingStatus, 'REVIEW'), "REVIEW state does not exist"
        assert hasattr(ProcessingStatus, 'COMPLETED'), "COMPLETED state does not exist"

        print("OK: Story status enum exists")

        # Test values
        assert ProcessingStatus.QA_PASS.value == "qa_pass", f"QA_PASS value error: {ProcessingStatus.QA_PASS.value}"
        print("OK: QA status values correct")

        return True
    except Exception as e:
        print(f"ERROR: ProcessingStatus test failed: {e}")
        traceback.print_exc()
        return False

def test_core_status_conversion():
    """Test core status conversion"""
    print("\n" + "=" * 60)
    print("Test 3: Core Status Conversion")
    print("=" * 60)

    try:
        from story_parser import core_status_to_processing, is_core_status_valid

        # Test conversion
        assert core_status_to_processing("Draft") == "pending", "Draft conversion failed"
        assert core_status_to_processing("Ready for Review") == "review", "Ready for Review conversion failed"
        assert core_status_to_processing("Done") == "completed", "Done conversion failed"

        print("OK: Core status conversion works")

        # Test validation
        assert is_core_status_valid("Draft"), "Draft validation failed"
        assert is_core_status_valid("Ready for Review"), "Ready for Review validation failed"
        assert is_core_status_valid("Done"), "Done validation failed"

        print("OK: Core status validation works")

        return True
    except Exception as e:
        print(f"ERROR: Core status conversion test failed: {e}")
        traceback.print_exc()
        return False

def test_normalize_status():
    """Test status normalization"""
    print("\n" + "=" * 60)
    print("Test 4: Status Normalization")
    print("=" * 60)

    try:
        from story_parser import _normalize_story_status

        # Test normalization
        assert _normalize_story_status("draft") == "Draft", "draft normalization failed"
        assert _normalize_story_status("Draft") == "Draft", "Draft normalization failed"
        assert _normalize_story_status("ready for review") == "Ready for Review", "ready for review normalization failed"

        print("OK: Status normalization works")

        return True
    except Exception as e:
        print(f"ERROR: Status normalization test failed: {e}")
        traceback.print_exc()
        return False

def test_agents():
    """Test agent initialization"""
    print("\n" + "=" * 60)
    print("Test 5: Agent Initialization")
    print("=" * 60)

    try:
        from qa_agent import QAAgent
        from dev_agent import DevAgent
        from sm_agent import SMAgent

        # Test QAAgent
        qa_agent = QAAgent()
        assert hasattr(qa_agent, 'status_parser'), "QAAgent missing status_parser"
        print("OK: QAAgent initialized successfully")

        # Test DevAgent
        dev_agent = DevAgent(use_claude=False)
        assert hasattr(dev_agent, 'status_parser'), "DevAgent missing status_parser"
        print("OK: DevAgent initialized successfully")

        # Test SMAgent
        sm_agent = SMAgent()
        assert hasattr(sm_agent, 'status_parser'), "SMAgent missing status_parser"
        print("OK: SMAgent initialized successfully")

        return True
    except Exception as e:
        print(f"ERROR: Agent initialization test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Status System Refactor Verification Tests")
    print("=" * 60)

    tests = [
        ("Import Test", test_imports),
        ("ProcessingStatus Test", test_processing_status),
        ("Core Status Conversion Test", test_core_status_conversion),
        ("Status Normalization Test", test_normalize_status),
        ("Agent Test", test_agents),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nERROR: {test_name} execution failed: {e}")
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\nSUCCESS: All tests passed! Status system refactor successful!")
        return 0
    else:
        print(f"\nWARNING: {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
