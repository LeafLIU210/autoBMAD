#!/usr/bin/env python3
"""验证清理是否彻底的脚本"""

import ast
import subprocess
import sys
from pathlib import Path


def check_no_kimi_session_manager():
    """检查是否还有 KimiSessionManager 引用"""
    result = subprocess.run(
        ["grep", "-rn", "KimiSessionManager", "--include=*.py", "autoBMAD/"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        # Filter out comments that mention "KimiSessionManager removed"
        lines = result.stdout.strip().split('\n')
        real_matches = []
        for line in lines:
            if 'KimiSessionManager removed' in line or line.strip().startswith('#'):
                continue
            real_matches.append(line)
        
        if real_matches:
            print("ERROR: 发现 KimiSessionManager 残留引用:")
            for line in real_matches:
                print(line)
            return False
    
    print("OK: KimiSessionManager 无残留")
    return True


def check_no_update_pipeline_status():
    """检查是否还有 update_pipeline_status 调用"""
    result = subprocess.run(
        ["grep", "-rn", "update_pipeline_status", "--include=*.py", "autoBMAD/"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print("ERROR: 发现 update_pipeline_status 残留调用:")
        print(result.stdout)
        return False
    print("OK: update_pipeline_status 无残留")
    return True


def check_no_kimi_env_vars_in_config():
    """检查 config.py 是否还读取 KIMI_*"""
    config_file = Path("autoBMAD/docuswarm/config.py")
    source = config_file.read_text()
    
    if "KIMI_API_KEY" in source or "KIMI_BASE_URL" in source:
        print("ERROR: config.py 仍包含 KIMI_* 引用")
        return False
    print("OK: config.py 无 KIMI_* 引用")
    return True


def check_no_claude_env_vars_in_session_manager():
    """检查 session_manager.py 是否还读取 CLAUDE_*"""
    sm_file = Path("autoBMAD/docuswarm/llm/session_manager.py")
    source = sm_file.read_text()
    
    if "CLAUDE_API_KEY" in source or "CLAUDE_BASE_URL" in source:
        print("ERROR: session_manager.py 仍包含 CLAUDE_* 引用")
        return False
    print("OK: session_manager.py 无 CLAUDE_* 引用")
    return True


def check_models_directory_removed():
    """检查 models 目录是否已删除"""
    models_dir = Path("autoBMAD/docuswarm/models")
    if models_dir.exists():
        print(f"ERROR: models 目录仍存在: {models_dir}")
        return False
    print("OK: models 目录已删除")
    return True


def check_no_deprecation_warnings():
    """检查 docuswarm 模块是否有 DeprecationWarning"""
    result = subprocess.run(
        ["grep", "-rn", "DeprecationWarning", "--include=*.py", "autoBMAD/docuswarm/"],
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print("ERROR: 发现 DeprecationWarning:")
        print(result.stdout)
        return False
    print("OK: docuswarm 模块无 DeprecationWarning")
    return True


def check_orchestrator_uses_session_manager():
    """检查 orchestrator 是否使用 SessionManager"""
    orch_file = Path("autoBMAD/docuswarm/pipeline/orchestrator.py")
    source = orch_file.read_text(encoding='utf-8')
    
    # Check for KimiSessionManager in actual code (not comments)
    for line in source.split('\n'):
        if 'KimiSessionManager' in line and not line.strip().startswith('#'):
            print("ERROR: orchestrator.py 仍包含 KimiSessionManager 代码引用")
            return False
    
    if "SessionManager" not in source:
        print("ERROR: orchestrator.py 未导入 SessionManager")
        return False
    print("OK: orchestrator.py 使用 SessionManager")
    return True


def check_escalation_uses_update_pipeline_state():
    """检查 escalation 是否使用 update_pipeline_state"""
    esc_file = Path("autoBMAD/docuswarm/pipeline/escalation.py")
    source = esc_file.read_text()
    
    if "update_pipeline_status" in source:
        print("ERROR: escalation.py 仍包含 update_pipeline_status")
        return False
    if "update_pipeline_state" not in source:
        print("ERROR: escalation.py 未使用 update_pipeline_state")
        return False
    print("OK: escalation.py 使用 update_pipeline_state")
    return True


def main():
    """运行所有检查"""
    checks = [
        check_no_kimi_session_manager,
        check_no_update_pipeline_status,
        check_no_kimi_env_vars_in_config,
        check_no_claude_env_vars_in_session_manager,
        check_models_directory_removed,
        check_no_deprecation_warnings,
        check_orchestrator_uses_session_manager,
        check_escalation_uses_update_pipeline_state,
    ]
    
    all_passed = all(check() for check in checks)
    
    if all_passed:
        print("\n[PASS] 所有清理检查通过！")
        return 0
    else:
        print("\n[FAIL] 部分检查未通过，请继续清理")
        return 1


if __name__ == "__main__":
    sys.exit(main())
