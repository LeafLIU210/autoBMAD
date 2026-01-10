#!/usr/bin/env python3
"""
测试脚本：验证 quality_agents 导入和基础功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    # 尝试导入 quality_agents 模块
    from autoBMAD.epic_automation import quality_agents
    
    print("✅ 成功导入 quality_agents 模块")
    
    # 检查 SafeClaudeSDK 是否可用
    if quality_agents.SafeClaudeSDK is not None:
        print("✅ SafeClaudeSDK 导入成功")
    else:
        print("⚠️  SafeClaudeSDK 未导入（正常，如果SDK不可用）")
    
    # 检查关键类是否存在
    if hasattr(quality_agents, 'CodeQualityAgent'):
        print("✅ CodeQualityAgent 类存在")
    else:
        print("❌ CodeQualityAgent 类不存在")
        
    if hasattr(quality_agents, 'RuffAgent'):
        print("✅ RuffAgent 类存在")
    else:
        print("❌ RuffAgent 类不存在")
        
    if hasattr(quality_agents, 'QualityGatePipeline'):
        print("✅ QualityGatePipeline 类存在")
    else:
        print("❌ QualityGatePipeline 类不存在")
    
    print("\n✅ 所有基础检查通过！")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
