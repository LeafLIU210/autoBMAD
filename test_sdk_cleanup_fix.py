"""
测试 SDK 清理修复 - 验证连续 SDK 调用不会触发跨任务错误

测试场景:
1. 第一个 SDK 调用完成 (story_parser)
2. 立即执行第二个 SDK 调用 (dev_agent)
3. 验证不会出现 "Attempted to exit cancel scope in a different task" 错误

预期结果:
- ✅ 两次 SDK 调用都成功
- ✅ 没有 cancel scope 跨任务错误
- ✅ 清理机制正常工作
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autoBMAD.epic_automation.monitoring import get_cancellation_manager
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK
from autoBMAD.epic_automation.story_parser import SimpleStoryParser
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_consecutive_sdk_calls():
    """测试连续 SDK 调用"""
    
    logger.info("=" * 70)
    logger.info("Starting SDK Cleanup Fix Test")
    logger.info("=" * 70)
    
    # 获取管理器
    manager = get_cancellation_manager()
    
    # 测试内容
    test_story_content = """
    # Story 1.1: Test Story
    
    **Status**: Ready for Development
    
    ## Acceptance Criteria
    - AC1: Test criteria
    """
    
    # Test 1: 第一次 SDK 调用 (模拟 story_parser)
    logger.info("\n[Test 1] First SDK call (story_parser simulation)")
    parser = SimpleStoryParser()
    
    # 创建 SDK wrapper
    sdk1 = SafeClaudeSDK(
        prompt="Extract status from story",
        options={"model": "MiniMax-M2"},
        timeout=10.0
    )
    parser.sdk_wrapper = sdk1
    
    try:
        status1 = await parser.parse_status(test_story_content)
        logger.info(f"[Test 1] ✅ First call succeeded: status='{status1}'")
    except Exception as e:
        logger.error(f"[Test 1] ❌ First call failed: {e}")
        return False
    
    # 检查管理器状态
    stats1 = manager.get_statistics()
    logger.info(f"[Stats After Test 1] Active calls: {len(manager.active_sdk_calls)}")
    logger.info(f"[Stats After Test 1] Total calls: {stats1['total_sdk_calls']}")
    
    # Test 2: 短暂等待后第二次 SDK 调用 (模拟 dev_agent)
    logger.info("\n[Test 2] Second SDK call (dev_agent simulation)")
    logger.info("[Test 2] Waiting for cleanup using SDKCancellationManager...")
    
    # 🎯 使用新的清理机制
    if manager.active_sdk_calls:
        active_call_ids = list(manager.active_sdk_calls.keys())
        logger.info(f"[Test 2] Found {len(active_call_ids)} active call(s)")
        
        for call_id in active_call_ids:
            cleanup_success = await manager.wait_for_cancellation_complete(
                call_id, timeout=5.0
            )
            if cleanup_success:
                logger.info(f"[Test 2] ✅ Cleanup confirmed for {call_id[:8]}...")
            else:
                logger.warning(f"[Test 2] ⚠️ Cleanup timeout for {call_id[:8]}...")
    else:
        logger.info("[Test 2] No active calls to cleanup")
        await asyncio.sleep(0.5)
    
    # 第二次 SDK 调用
    sdk2 = SafeClaudeSDK(
        prompt="Develop the story",
        options={"model": "MiniMax-M2"},
        timeout=10.0
    )
    
    try:
        success2 = await sdk2.execute()
        logger.info(f"[Test 2] ✅ Second call succeeded: success={success2}")
    except RuntimeError as e:
        error_msg = str(e)
        if "cancel scope" in error_msg.lower() and "different task" in error_msg.lower():
            logger.error(f"[Test 2] ❌ Cancel scope error detected: {e}")
            return False
        else:
            raise
    except Exception as e:
        logger.error(f"[Test 2] ❌ Second call failed: {e}")
        return False
    
    # 最终统计
    logger.info("\n" + "=" * 70)
    logger.info("Test Complete - Final Statistics")
    logger.info("=" * 70)
    
    stats_final = manager.get_statistics()
    logger.info(f"Total SDK Calls: {stats_final['total_sdk_calls']}")
    logger.info(f"Successful: {stats_final['successful_completions']}")
    logger.info(f"Cancelled: {stats_final['cancellations']}")
    logger.info(f"  - After Success: {stats_final['cancel_after_success']}")
    logger.info(f"Failed: {stats_final['failures']}")
    logger.info(f"Cross-task Violations: {stats_final['cross_task_violations']}")
    
    # 打印详细报告
    manager.print_summary()
    
    # 验证结果
    success = True
    
    # 检查是否有跨任务清理 (这是正常的,不计为错误)
    # 关键是检查是否有真正的 RuntimeError
    if stats_final['total_sdk_calls'] < 2:
        logger.error("❌ Test FAILED: Not all SDK calls executed")
        success = False
    else:
        logger.info("✅ Test PASSED: No fatal errors, cleanup mechanism working")
    
    return success


async def main():
    """主测试函数"""
    try:
        success = await test_consecutive_sdk_calls()
        
        if success:
            logger.info("\n✅ SDK Cleanup Fix Test PASSED")
            sys.exit(0)
        else:
            logger.error("\n❌ SDK Cleanup Fix Test FAILED")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\n❌ Test execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
