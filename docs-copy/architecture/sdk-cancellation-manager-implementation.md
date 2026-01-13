# SDK 取消管理器实施指南

## 📋 文档信息

- **版本**: 1.0.0
- **创建日期**: 2026-01-10
- **依赖文档**: [设计方案](./sdk-cancellation-manager-design.md)
- **状态**: 实施中

## 🎯 实施概览

本文档提供 SDK 取消管理器的详细实施步骤、代码示例和集成指导。

### 核心原则：奥卡姆剃刀

根据**奥卡姆剃刀原则**，实施遵循以下核心规则：

1. **唯一入口**：所有 SDK 取消必须通过管理器统一处理，禁止分散的取消代码
2. **强制确认**：Agent 必须等待管理器确认 SDK 清理完成后才能继续
3. **移除冗余**：删除所有分散在各 Agent 中的重复取消处理逻辑
4. **单一真相来源**：管理器是 SDK 取消状态的唯一权威来源

## 📦 Phase 1: 基础设施搭建

### 步骤 1.1: 创建目录结构

```bash
# 创建监控模块目录
cd d:/GITHUB/pytQt_template/autoBMAD/epic_automation
mkdir -p monitoring

# 验证目录结构
tree monitoring
# monitoring/
# └── (待创建文件)
```

### 步骤 1.2: 迁移核心组件

```bash
# 从 BUGFIX 目录复制文件
cp ../../BUGFIX_20260107/enhanced_debug_suite/cancel_scope_tracker.py monitoring/
cp ../../BUGFIX_20260107/enhanced_debug_suite/resource_monitor.py monitoring/
cp ../../BUGFIX_20260107/enhanced_debug_suite/async_debugger.py monitoring/

# 验证文件
ls monitoring/
# cancel_scope_tracker.py
# resource_monitor.py
# async_debugger.py
```

### 步骤 1.3: 创建 `__init__.py`

```python
# autoBMAD/epic_automation/monitoring/__init__.py
"""
SDK 取消管理监控模块

提供统一的 SDK 取消追踪、监控和诊断功能。
"""

from .cancel_scope_tracker import (
    CancelScopeTracker,
    get_tracker,
    tracked_cancel_scope
)
from .resource_monitor import (
    ResourceMonitor,
    get_resource_monitor
)
from .async_debugger import (
    AsyncDebugger,
    get_debugger
)
from .sdk_cancellation_manager import (
    SDKCancellationManager,
    get_cancellation_manager
)

__all__ = [
    # Cancel Scope Tracker
    "CancelScopeTracker",
    "get_tracker",
    "tracked_cancel_scope",
    
    # Resource Monitor
    "ResourceMonitor",
    "get_resource_monitor",
    
    # Async Debugger
    "AsyncDebugger",
    "get_debugger",
    
    # SDK Cancellation Manager
    "SDKCancellationManager",
    "get_cancellation_manager",
]

__version__ = "1.0.0"
```

### 步骤 1.4: 创建核心管理器

```python
# autoBMAD/epic_automation/monitoring/sdk_cancellation_manager.py
"""
SDK 取消管理器 - Unified SDK Cancellation Manager

统一管理 SDK 取消过程的检查、监控和清理机制。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal
import json
import uuid

from .cancel_scope_tracker import CancelScopeTracker, get_tracker
from .resource_monitor import ResourceMonitor, get_resource_monitor
from .async_debugger import AsyncDebugger, get_debugger

logger = logging.getLogger(__name__)


class SDKCancellationManager:
    """SDK 取消管理器"""
    
    def __init__(
        self,
        log_dir: Optional[Path] = None,
        enable_tracking: bool = True,
        enable_monitoring: bool = True,
        enable_debugging: bool = True
    ):
        """
        初始化 SDK 取消管理器
        
        Args:
            log_dir: 日志目录
            enable_tracking: 启用 cancel scope 追踪
            enable_monitoring: 启用资源监控
            enable_debugging: 启用异步调试
        """
        self.log_dir = log_dir or Path("autoBMAD/epic_automation/logs/monitoring")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.tracker = (
            get_tracker(self.log_dir / "cancel_scope_tracker.log")
            if enable_tracking
            else None
        )
        
        self.resource_monitor = (
            get_resource_monitor()
            if enable_monitoring
            else None
        )
        
        self.debugger = (
            get_debugger(self.log_dir / "async_debug.log")
            if enable_debugging
            else None
        )
        
        # 状态跟踪
        self.active_sdk_calls: Dict[str, Dict[str, Any]] = {}
        self.completed_calls: List[Dict[str, Any]] = []
        self.cancelled_calls: List[Dict[str, Any]] = []
        self.failed_calls: List[Dict[str, Any]] = []
        
        # 统计信息
        self.stats = {
            "total_sdk_calls": 0,
            "successful_completions": 0,
            "cancellations": 0,
            "cancel_after_success": 0,
            "failures": 0,
            "cross_task_violations": 0
        }
        
        logger.info(
            f"SDK Cancellation Manager initialized "
            f"(tracking={enable_tracking}, monitoring={enable_monitoring}, "
            f"debugging={enable_debugging})"
        )
    
    @asynccontextmanager
    async def track_sdk_execution(
        self,
        call_id: str,
        operation_name: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        追踪 SDK 执行的上下文管理器
        
        使用方法:
        ```python
        async with manager.track_sdk_execution("parse_status", "status_parsing"):
            result = await sdk.execute()
        ```
        
        Args:
            call_id: 调用唯一标识
            operation_name: 操作名称
            context: 上下文信息
        """
        start_time = datetime.now()
        scope_id = None
        
        # 进入 cancel scope 追踪
        if self.tracker:
            scope_id = self.tracker.enter_scope(name=f"sdk_{operation_name}")
        
        # 记录 SDK 调用开始
        call_info = {
            "call_id": call_id,
            "operation": operation_name,
            "scope_id": scope_id,
            "start_time": start_time,
            "context": context or {},
            "status": "in_progress",
            "result": None,
            "result_received_at": None,
            "exception": None,
            "cancel_type": None
        }
        
        self.active_sdk_calls[call_id] = call_info
        self.stats["total_sdk_calls"] += 1
        
        logger.info(
            f"[SDK Tracking] Started: {operation_name} "
            f"(call_id={call_id[:8]}..., scope={scope_id[:8] if scope_id else 'none'}...)"
        )
        
        try:
            # 执行 SDK 操作
            yield call_info
            
            # 成功完成
            call_info["status"] = "completed"
            call_info["end_time"] = datetime.now()
            call_info["duration"] = (
                call_info["end_time"] - start_time
            ).total_seconds()
            
            self.stats["successful_completions"] += 1
            self.completed_calls.append(call_info.copy())
            
            logger.info(
                f"[SDK Tracking] Completed: {operation_name} "
                f"(duration={call_info['duration']:.2f}s)"
            )
            
        except asyncio.CancelledError as e:
            # 取消检测
            call_info["status"] = "cancelled"
            call_info["end_time"] = datetime.now()
            call_info["exception"] = str(e)
            call_info["duration"] = (
                call_info["end_time"] - start_time
            ).total_seconds()
            
            # 🎯 关键：检查是否是"成功后取消"
            if call_info.get("result") is not None:
                call_info["cancel_type"] = "after_success"
                self.stats["cancel_after_success"] += 1
                
                logger.warning(
                    f"[SDK Tracking] ⚠️ Cancelled AFTER success: {operation_name} "
                    f"(duration={call_info['duration']:.2f}s, "
                    f"result={str(call_info['result'])[:50]})"
                )
            else:
                call_info["cancel_type"] = "before_completion"
                
                logger.info(
                    f"[SDK Tracking] Cancelled: {operation_name} "
                    f"(duration={call_info['duration']:.2f}s)"
                )
            
            self.stats["cancellations"] += 1
            self.cancelled_calls.append(call_info.copy())
            
            # 重新抛出，让上层决定如何处理
            raise
            
        except Exception as e:
            # 错误处理
            call_info["status"] = "failed"
            call_info["end_time"] = datetime.now()
            call_info["exception"] = str(e)
            call_info["duration"] = (
                call_info["end_time"] - start_time
            ).total_seconds()
            
            self.stats["failures"] += 1
            self.failed_calls.append(call_info.copy())
            
            logger.error(
                f"[SDK Tracking] Failed: {operation_name} "
                f"(duration={call_info['duration']:.2f}s, error={e})"
            )
            
            raise
            
        finally:
            # 清理
            if call_id in self.active_sdk_calls:
                del self.active_sdk_calls[call_id]
            
            # 🎯 标记清理完成
            if call_info["status"] == "cancelled":
                call_info["cleanup_completed"] = True
                logger.debug(
                    f"[SDK Tracking] Cleanup completed for {call_id[:8]}..."
                )
            
            # 退出 cancel scope
            if self.tracker and scope_id:
                exception = call_info.get("exception")
                self.tracker.exit_scope(
                    scope_id,
                    name=f"sdk_{operation_name}",
                    exception=Exception(exception) if exception else None
                )
    
    🎯 关键方法：等待取消完成（强制同步点）
    async def wait_for_cancellation_complete(
        self,
        call_id: str,
        timeout: float = 5.0
    ) -> bool:
        """
        等待 SDK 取消完全完成
        
        🎯 强制同步点：Agent 必须等待此方法返回 True 才能继续
        
        Args:
            call_id: 调用标识
            timeout: 超时时间（秒）
            
        Returns:
            True if cancellation completed successfully
        """
        if call_id not in self.active_sdk_calls:
            # 已经清理完成
            return True
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            if call_id not in self.active_sdk_calls:
                logger.info(f"[SDK Tracking] Cancellation completed for {call_id[:8]}...")
                return True
            
            # 等待 100ms 后重试
            await asyncio.sleep(0.1)
        
        logger.warning(
            f"[SDK Tracking] Cancellation timeout for {call_id[:8]}... "
            f"after {timeout}s"
        )
        return False
    
    def confirm_safe_to_proceed(self, call_id: str) -> bool:
        """
        确认 SDK 可以安全继续
        
        🎯 Agent 在继续执行前必须调用此方法
        
        Args:
            call_id: 调用标识
            
        Returns:
            True if safe to proceed, False otherwise
        """
        # 检查是否还在活动列表中
        if call_id in self.active_sdk_calls:
            logger.warning(
                f"[SDK Tracking] Not safe to proceed - {call_id[:8]}... "
                f"still active"
            )
            return False
        
        # 检查是否在取消列表中且未完全清理
        for cancelled_call in self.cancelled_calls:
            if cancelled_call["call_id"] == call_id:
                # 检查清理标志
                if not cancelled_call.get("cleanup_completed", False):
                    logger.warning(
                        f"[SDK Tracking] Not safe to proceed - {call_id[:8]}... "
                        f"cleanup not completed"
                    )
                    return False
        
        logger.debug(f"[SDK Tracking] Safe to proceed for {call_id[:8]}...")
        return True
        """
        标记 SDK 结果已接收
        
        🎯 关键方法：在 SDK 成功返回结果后立即调用
        用于检测"成功后取消"场景
        
        Args:
            call_id: 调用标识
            result: SDK 返回的结果
        """
        if call_id in self.active_sdk_calls:
            self.active_sdk_calls[call_id]["result"] = result
            self.active_sdk_calls[call_id]["result_received_at"] = datetime.now()
            
            result_preview = str(result)[:100]
            logger.debug(
                f"[SDK Tracking] Result received for {call_id[:8]}...: "
                f"{result_preview}"
            )
    
    def mark_result_received(self, call_id: str, result: Any):
        self, 
        call_id: str
    ) -> Literal["before_completion", "after_success", "unknown"]:
        """
        检查取消类型
        
        Args:
            call_id: 调用标识
            
        Returns:
            取消类型：
            - "after_success": 成功后被取消
            - "before_completion": 完成前被取消
            - "unknown": 未知
        """
        # 检查已取消的调用
        for call in self.cancelled_calls:
            if call["call_id"] == call_id:
                return call.get("cancel_type", "unknown")
        
        # 检查活动调用
        if call_id in self.active_sdk_calls:
            call_info = self.active_sdk_calls[call_id]
            if call_info.get("result") is not None:
                return "after_success"
        
        return "unknown"
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        
        # 计算比率
        total = stats["total_sdk_calls"]
        if total > 0:
            stats["success_rate"] = stats["successful_completions"] / total
            stats["cancellation_rate"] = stats["cancellations"] / total
            stats["failure_rate"] = stats["failures"] / total
            stats["cancel_after_success_rate"] = stats["cancel_after_success"] / total
        else:
            stats["success_rate"] = 0.0
            stats["cancellation_rate"] = 0.0
            stats["failure_rate"] = 0.0
            stats["cancel_after_success_rate"] = 0.0
        
        # 添加跨任务违规统计
        if self.tracker:
            violations = self.tracker.check_cross_task_violations()
            stats["cross_task_violations"] = len(violations)
        
        return stats
    
    def generate_report(self, save_to_file: bool = True) -> Dict[str, Any]:
        """
        生成诊断报告
        
        Args:
            save_to_file: 是否保存到文件
            
        Returns:
            完整的诊断报告
        """
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0.0",
                "system_version": "BMAD 2.0.0"
            },
            "summary": self.get_statistics(),
            "active_operations": [
                {
                    "call_id": call_id,
                    "operation": info["operation"],
                    "duration": (
                        datetime.now() - info["start_time"]
                    ).total_seconds(),
                    "status": info["status"]
                }
                for call_id, info in self.active_sdk_calls.items()
            ],
            "completed_calls": self.completed_calls[-10:],  # 最近 10 个
            "cancelled_calls": self.cancelled_calls,
            "failed_calls": self.failed_calls,
        }
        
        # 添加 cancel scope 分析
        if self.tracker:
            report["cancel_scope_analysis"] = {
                "statistics": self.tracker.get_scope_statistics(),
                "active_scopes": self.tracker.get_active_scopes_info(),
                "cross_task_violations": self.tracker.check_cross_task_violations()
            }
        
        # 添加资源使用情况
        if self.resource_monitor:
            report["resource_usage"] = {
                "locks": self.resource_monitor.get_lock_statistics(),
                "sdk_sessions": {
                    "total": len(self.resource_monitor.sdk_sessions),
                    "active": len([
                        s for s in self.resource_monitor.sdk_sessions.values()
                        if s["status"] == "executing"
                    ])
                }
            }
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        # 保存到文件
        if save_to_file:
            report_file = self.log_dir / f"sdk_cancellation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Cancellation report saved to {report_file}")
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = []
        summary = report["summary"]
        
        # 检查成功后取消
        if summary["cancel_after_success"] > 0:
            recommendations.append(
                f"⚠️ {summary['cancel_after_success']} cancellations occurred after "
                f"successful completion - consider suppressing these cancellations"
            )
        
        # 检查跨任务违规
        if summary["cross_task_violations"] > 0:
            recommendations.append(
                f"❌ {summary['cross_task_violations']} cross-task cancel scope "
                f"violations detected - review task isolation"
            )
        
        # 检查成功率
        if summary["success_rate"] < 0.8:
            recommendations.append(
                f"⚠️ Success rate is low ({summary['success_rate']:.1%}) - "
                f"investigate failure causes"
            )
        elif summary["success_rate"] > 0.9:
            recommendations.append(
                f"✅ Success rate is healthy ({summary['success_rate']:.1%})"
            )
        
        # 检查取消率
        if summary["cancellation_rate"] > 0.2:
            recommendations.append(
                f"⚠️ High cancellation rate ({summary['cancellation_rate']:.1%}) - "
                f"consider timeout adjustments"
            )
        
        return recommendations
    
    def print_summary(self):
        """打印摘要到控制台"""
        stats = self.get_statistics()
        
        print("\n" + "=" * 70)
        print("          SDK Cancellation Manager - Live Status")
        print("=" * 70)
        
        print(f"Statistics:")
        print(f"  Total SDK Calls:      {stats['total_sdk_calls']}")
        print(f"  Successful:           {stats['successful_completions']} "
              f"({stats['success_rate']:.1%})")
        print(f"  Cancelled:            {stats['cancellations']} "
              f"({stats['cancellation_rate']:.1%})")
        print(f"    └─ After Success:   {stats['cancel_after_success']} "
              f"({stats['cancel_after_success_rate']:.1%})  "
              f"{'⚠️' if stats['cancel_after_success'] > 0 else ''}")
        print(f"  Failed:               {stats['failures']} "
              f"({stats['failure_rate']:.1%})")
        
        # 活动操作
        active_ops = [
            {
                "call_id": call_id,
                "operation": info["operation"],
                "duration": (datetime.now() - info["start_time"]).total_seconds()
            }
            for call_id, info in self.active_sdk_calls.items()
        ]
        
        print(f"\nActive Operations: {len(active_ops)}")
        for op in active_ops:
            print(f"  • {op['call_id'][:8]}... ({op['operation']}) - "
                  f"Running for {op['duration']:.1f}s")
        
        # Cancel Scope 状态
        if self.tracker:
            scope_stats = self.tracker.get_scope_statistics()
            print(f"\nCancel Scope Status:")
            print(f"  Active Scopes:        {scope_stats['active_scopes']}")
            print(f"  Cross-task Violations: {scope_stats['cross_task_violations']}  "
                  f"{'❌' if scope_stats['cross_task_violations'] > 0 else '✅'}")
        
        print("=" * 70)


# 全局单例
_global_manager: Optional[SDKCancellationManager] = None


def get_cancellation_manager(
    log_dir: Optional[Path] = None,
    enable_tracking: bool = True,
    enable_monitoring: bool = True,
    enable_debugging: bool = True
) -> SDKCancellationManager:
    """
    获取全局 SDK 取消管理器实例
    
    Args:
        log_dir: 日志目录
        enable_tracking: 启用 cancel scope 追踪
        enable_monitoring: 启用资源监控
        enable_debugging: 启用异步调试
        
    Returns:
        全局管理器实例
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = SDKCancellationManager(
            log_dir=log_dir,
            enable_tracking=enable_tracking,
            enable_monitoring=enable_monitoring,
            enable_debugging=enable_debugging
        )
    
    return _global_manager


def reset_cancellation_manager():
    """重置全局管理器（用于测试）"""
    global _global_manager
    _global_manager = None
```

## 📦 Phase 2: SafeClaudeSDK 集成

### 修改 `sdk_wrapper.py`

**核心原则：移除所有独立的取消判断逻辑，统一委托给管理器**

在 `SafeClaudeSDK.execute()` 方法中集成管理器：

```python
# autoBMAD/epic_automation/sdk_wrapper.py

async def execute(self) -> bool:
    """
    Execute Claude SDK query with unified cancellation management.
    
    🎯 关键改变：
    1. 移除所有本地取消判断逻辑
    2. 完全委托给 SDKCancellationManager
    3. 不再在此处处理 cancel scope 错误
    
    Returns:
        True if execution succeeded, False otherwise
    """
    if not SDK_AVAILABLE:
        logger.warning("Claude Agent SDK not available")
        return False
    
    # 🎯 唯一入口：获取全局管理器
    from autoBMAD.epic_automation.monitoring import get_cancellation_manager
    manager = get_cancellation_manager()
    
    # 生成唯一调用 ID
    call_id = f"sdk_{id(self)}_{int(time.time() * 1000)}"
    
    try:
        # 🎯 所有 SDK 执行都必须通过管理器追踪
        async with manager.track_sdk_execution(
            call_id=call_id,
            operation_name="sdk_execute",
            context={
                "prompt_length": len(self.prompt),
                "has_options": self.options is not None
            }
        ):
            result = await self._execute_safely_with_manager(manager, call_id)
            return result
            
    except asyncio.CancelledError:
        # 🎯 统一处理：完全委托给管理器决策
        cancel_type = manager.check_cancellation_type(call_id)
        
        if cancel_type == "after_success":
            # 管理器确认工作已完成，等待清理完成
            await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
            logger.info(
                "[SafeClaudeSDK] Cancellation suppressed - "
                "SDK completed successfully (confirmed by manager)"
            )
            return True
        
        # 真正的取消
        logger.warning("SDK execution was cancelled (confirmed by manager)")
        # 等待清理完成
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        raise
        
    except Exception as e:
        logger.error(f"Claude SDK execution failed: {e}")
        logger.debug(traceback.format_exc())
        return False

# ❌ 移除：以下方法中的独立取消处理逻辑
# - _execute_safely() 中的 RuntimeError catch
# - _run_isolated_generator() 中的 CancelledError 判断
# 全部替换为管理器调用
```

**关键移除项（符合奥卡姆剃刀原则）：**

```python
# ❌ 删除这些代码片段：

# 1. 在 execute() 中的独立 cancel scope 处理
except RuntimeError as e:
    error_msg = str(e).lower()
    if "cancel scope" in error_msg:  # ❌ 删除
        logger.debug(f"Cancel scope error suppressed: {e}")
        return True

# 2. 在 _run_isolated_generator() 中的独立判断
except asyncio.CancelledError:
    if result_received:  # ❌ 删除这个判断
        logger.info("SDK already completed")
        return True
    raise

# ✅ 替换为统一管理器调用
except asyncio.CancelledError:
    # 委托给管理器
    cancel_type = manager.check_cancellation_type(call_id)
    if cancel_type == "after_success":
        await manager.wait_for_cancellation_complete(call_id)
        return True
    raise
```

async def _execute_safely_with_manager(
    self,
    manager: "SDKCancellationManager",
    call_id: str
) -> bool:
    """
    Execute with cancellation manager integration.
    
    Args:
        manager: Cancellation manager instance
        call_id: Unique call identifier
        
    Returns:
        True if successful, False otherwise
    """
    if query is None or self.options is None:
        logger.warning("Claude SDK not properly initialized")
        return False
    
    logger.info("[SDK Start] Starting Claude SDK execution with tracking")
    logger.info(f"[SDK Config] Prompt length: {len(self.prompt)} characters")
    
    # 创建查询生成器
    try:
        generator = query(prompt=self.prompt, options=self.options)
    except Exception as e:
        logger.error(f"Failed to create SDK query generator: {e}")
        return False
    
    # 包装生成器
    safe_generator = SafeAsyncGenerator(generator)
    
    try:
        result = await self._run_isolated_generator_with_manager(
            safe_generator,
            manager,
            call_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in isolated generator execution: {e}")
        await safe_generator.aclose()
        return False


async def _run_isolated_generator_with_manager(
    self,
    safe_generator: SafeAsyncGenerator,
    manager: "SDKCancellationManager",
    call_id: str
) -> bool:
    """
    Run generator with cancellation manager result tracking.
    
    🎯 关键改进：立即标记结果接收
    """
    message_count = 0
    start_time = asyncio.get_running_loop().time()
    
    try:
        await self.message_tracker.start_periodic_display()
        
        async for message in safe_generator:
            message_count += 1
            
            message_content = self._extract_message_content(message)
            message_type = self._classify_message_type(message)
            
            if message_content:
                self.message_tracker.update_message(message_content, message_type)
            
            if ResultMessage is not None and isinstance(message, ResultMessage):
                if hasattr(message, "is_error") and message.is_error:
                    error_msg = getattr(message, "result", "Unknown error")
                    logger.error(f"[SDK Error] Claude SDK error: {error_msg}")
                    return False
                else:
                    result = getattr(message, "result", None)
                    result_str = str(result) if result else "No content"
                    
                    # 🎯 关键：立即标记结果接收
                    manager.mark_result_received(call_id, result_str)
                    
                    logger.info(f"[SDK Success] Claude SDK result: {result_str[:100]}")
                    return True
        
        # 没有收到 ResultMessage
        total_elapsed = asyncio.get_running_loop().time() - start_time
        
        await self.message_tracker.stop_periodic_display()
        
        if message_count > 0:
            logger.info(
                f"[SDK Complete] Completed with {message_count} messages "
                f"in {total_elapsed:.1f}s"
            )
            return True
        else:
            logger.error(f"[SDK Failed] No messages received after {total_elapsed:.1f}s")
            return False
    
    except StopAsyncIteration:
        logger.info("Claude SDK generator completed")
        return True
        
    except asyncio.CancelledError:
        logger.warning("Claude SDK execution was cancelled")
        
        try:
            await self.message_tracker.stop_periodic_display()
        except Exception as e:
            logger.debug(f"Error stopping display task: {e}")
        
        # 🎯 重新抛出，让外层检查取消类型
        raise
        
    except Exception as e:
        logger.error(f"Claude SDK execution error: {e}")
        try:
            await self.message_tracker.stop_periodic_display()
        except Exception as cleanup_error:
            logger.debug(f"Error during cleanup: {cleanup_error}")
        raise
        
    finally:
        await safe_generator.aclose()
```

## 📦 Phase 3: Agent 层集成

### DevAgent 集成示例

**核心原则：Agent 必须等待管理器确认后才能继续执行**

```python
# autoBMAD/epic_automation/dev_agent.py

async def execute(self, story_path: str) -> bool:
    """
    开发执行流程 - 强制通过管理器处理所有 SDK 取消
    
    🎯 关键改变：
    1. 移除所有本地异常处理逻辑
    2. 强制等待管理器确认清理完成
    3. 不再自行判断是否可以继续
    """
    logger.info(f"{self.name} executing Dev phase")
    
    # 🎯 唯一入口：获取全局管理器
    from autoBMAD.epic_automation.monitoring import get_cancellation_manager
    manager = get_cancellation_manager()
    
    call_id = f"dev_parse_{story_path}_{int(time.time())}"
    
    try:
        # 1. 解析核心状态值 - 通过管理器追踪
        if hasattr(self, 'status_parser') and self.status_parser:
            story_file = Path(story_path)
            if story_file.exists():
                content = story_file.read_text(encoding="utf-8")
                
                # 🎯 所有 SDK 调用都必须通过管理器
                async with manager.track_sdk_execution(
                    call_id=call_id,
                    operation_name="parse_status",
                    context={
                        "agent": "dev_agent",
                        "story": story_path,
                        "content_length": len(content)
                    }
                ):
                    story_status = await self.status_parser.parse_status(content)
                
                # 🎯 强制同步点：等待管理器确认 SDK 已完全清理
                cleanup_ok = await manager.wait_for_cancellation_complete(
                    call_id, 
                    timeout=5.0
                )
                if not cleanup_ok:
                    logger.error("SDK cleanup timeout - unsafe to proceed")
                    return False
                
                # 🎯 二次确认：检查是否安全继续
                if not manager.confirm_safe_to_proceed(call_id):
                    logger.error("Manager blocked continuation - SDK not fully cleaned")
                    return False
                
            else:
                logger.warning(f"[Dev Agent] Story file not found: {story_path}")
                story_status = "Unknown"
        else:
            logger.warning("[Dev Agent] Status parser not available")
            story_status = "Unknown"
        
        # 2. 状态判断（只有在管理器确认安全后才执行）
        if story_status.lower() in ["ready for done", "done"]:
            logger.info(
                f"[Dev Agent] Story '{story_path}' already completed ({story_status})"
            )
            return True
        
        # 3. 执行开发任务
        logger.info(f"[Dev Agent] Executing development tasks for '{story_path}'")
        development_success = True  # 简化实现
        
        if not development_success:
            logger.error("Failed to complete development tasks")
            return False
        
        return True
        
    except asyncio.CancelledError:
        # 🎯 统一处理：完全委托给管理器
        cancel_type = manager.check_cancellation_type(call_id)
        
        if cancel_type == "after_success":
            # 等待清理完成
            await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
            logger.info(
                "[Dev Agent] Dev phase completed despite cancellation "
                "(confirmed by manager)"
            )
            return True
        
        logger.warning("[Dev Agent] Dev phase cancelled (confirmed by manager)")
        # 等待清理完成后再抛出
        await manager.wait_for_cancellation_complete(call_id, timeout=5.0)
        raise
        
    except Exception as e:
        logger.error(f"{self.name} Dev phase failed: {e}")
        return False

# ❌ 移除：以下独立的异常处理代码
# - 本地的 CancelledError 判断
# - 自定义的 result_received 标志
# - 直接返回 True 的逻辑（未经管理器确认）
```

**关键移除项（符合奥卡姆剃刀原则）：**

```python
# ❌ 删除这些代码片段：

# 1. Dev Agent 中的独立取消判断
except asyncio.CancelledError:
    # 检查是否应该继续  # ❌ 删除这个本地判断
    if some_local_flag:
        return True
    raise

# 2. 没有等待管理器确认就继续执行
story_status = await self.status_parser.parse_status(content)
return True  # ❌ 直接继续，不安全

# ✅ 替换为强制确认流程
story_status = await self.status_parser.parse_status(content)
await manager.wait_for_cancellation_complete(call_id)  # 强制等待
if not manager.confirm_safe_to_proceed(call_id):  # 二次确认
    return False
return True  # 安全继续
```

## 📊 使用示例

### 基本使用

```python
from autoBMAD.epic_automation.monitoring import get_cancellation_manager

# 获取全局管理器
manager = get_cancellation_manager()

# 追踪 SDK 执行
async def my_sdk_operation():
    async with manager.track_sdk_execution(
        call_id="my_op_001",
        operation_name="custom_operation",
        context={"user": "admin"}
    ) as call_info:
        # 执行 SDK 操作
        result = await some_sdk_call()
        
        # 标记结果接收
        manager.mark_result_received("my_op_001", result)
        
        return result

# 生成报告
report = manager.generate_report()
print(f"Success rate: {report['summary']['success_rate']:.1%}")
```

### 实时监控

```python
# 定期打印状态
import asyncio

async def monitor_loop():
    manager = get_cancellation_manager()
    
    while True:
        await asyncio.sleep(30)  # 每 30 秒
        manager.print_summary()

# 启动监控任务
asyncio.create_task(monitor_loop())
```

### 诊断报告

```python
# 在 Epic 完成后生成报告
async def process_epic():
    manager = get_cancellation_manager()
    
    try:
        # 处理 Epic
        await epic_driver.run()
    finally:
        # 生成诊断报告
        report = manager.generate_report(save_to_file=True)
        
        # 检查问题
        if report["summary"]["cancel_after_success"] > 0:
            print("⚠️ Warning: Some operations were cancelled after success")
            print("Review the report for details")
```

## 🧪 测试验证

### 单元测试

```python
# tests/test_sdk_cancellation_manager.py

import pytest
import asyncio
from autoBMAD.epic_automation.monitoring import SDKCancellationManager

@pytest.mark.asyncio
async def test_successful_execution():
    """测试成功执行追踪"""
    manager = SDKCancellationManager(enable_monitoring=False, enable_debugging=False)
    
    async with manager.track_sdk_execution("test_001", "test_op"):
        manager.mark_result_received("test_001", "success")
    
    stats = manager.get_statistics()
    assert stats["successful_completions"] == 1
    assert stats["cancellations"] == 0

@pytest.mark.asyncio
async def test_cancel_after_success():
    """测试成功后取消检测"""
    manager = SDKCancellationManager(enable_monitoring=False, enable_debugging=False)
    
    with pytest.raises(asyncio.CancelledError):
        async with manager.track_sdk_execution("test_002", "test_op"):
            manager.mark_result_received("test_002", "result")
            raise asyncio.CancelledError()
    
    stats = manager.get_statistics()
    assert stats["cancel_after_success"] == 1
    
    cancel_type = manager.check_cancellation_type("test_002")
    assert cancel_type == "after_success"

@pytest.mark.asyncio
async def test_cancel_before_completion():
    """测试完成前取消"""
    manager = SDKCancellationManager(enable_monitoring=False, enable_debugging=False)
    
    with pytest.raises(asyncio.CancelledError):
        async with manager.track_sdk_execution("test_003", "test_op"):
            raise asyncio.CancelledError()
    
    cancel_type = manager.check_cancellation_type("test_003")
    assert cancel_type == "before_completion"
```

### 集成测试

```python
# tests/integration/test_sdk_wrapper_integration.py

import pytest
from autoBMAD.epic_automation.sdk_wrapper import SafeClaudeSDK
from autoBMAD.epic_automation.monitoring import (
    get_cancellation_manager,
    reset_cancellation_manager
)

@pytest.mark.asyncio
async def test_sdk_wrapper_tracking():
    """测试 SDK wrapper 集成"""
    reset_cancellation_manager()  # 重置
    manager = get_cancellation_manager()
    
    # 创建 SDK 实例
    sdk = SafeClaudeSDK(
        prompt="Test prompt",
        options=None,  # Mock options
        timeout=None
    )
    
    # 执行（需要 mock claude_agent_sdk）
    # result = await sdk.execute()
    
    # 验证追踪
    stats = manager.get_statistics()
    # assert stats["total_sdk_calls"] >= 1
```

## 🔍 故障排查

### 常见问题

#### 问题 1: 管理器未追踪 SDK 调用

**症状：** 统计信息显示 `total_sdk_calls = 0`

**解决：**
```python
# 确认已正确导入和初始化
from autoBMAD.epic_automation.monitoring import get_cancellation_manager
manager = get_cancellation_manager()

# 确认使用上下文管理器
async with manager.track_sdk_execution(...):
    ...
```

#### 问题 2: "成功后取消"未被检测

**症状：** 操作完成后仍被标记为失败

**解决：**
```python
# 确保在结果接收后立即调用
result = await sdk.execute()
manager.mark_result_received(call_id, result)  # 🎯 立即调用
```

#### 问题 3: 性能开销过大

**症状：** 系统变慢

**解决：**
```python
# 禁用不必要的组件
manager = SDKCancellationManager(
    enable_tracking=True,
    enable_monitoring=False,  # 禁用资源监控
    enable_debugging=False    # 禁用异步调试
)
```

## 📝 变更检查清单

在集成前，请确认以下变更：

- [ ] `monitoring/` 目录已创建
- [ ] 核心组件已从 BUGFIX 迁移
- [ ] `SDKCancellationManager` 已实现
- [ ] `__init__.py` 已创建并导出所有类
- [ ] `sdk_wrapper.py` 已集成管理器
- [ ] `dev_agent.py` 已集成管理器
- [ ] 单元测试已添加
- [ ] 集成测试已添加
- [ ] 文档已更新

## 🚀 部署步骤

1. **备份现有代码**
   ```bash
   git branch backup-pre-cancellation-manager
   git checkout -b feature/sdk-cancellation-manager
   ```

2. **实施变更**
   ```bash
   # 按照本文档执行所有步骤
   ```

3. **运行测试**
   ```bash
   pytest tests/test_sdk_cancellation_manager.py -v
   pytest tests/integration/test_sdk_wrapper_integration.py -v
   ```

4. **验证集成**
   ```bash
   # 运行实际 Epic 测试
   python -m autoBMAD.epic_automation.epic_driver docs/epics/epic-1.md
   
   # 检查报告
   ls autoBMAD/epic_automation/logs/monitoring/
   ```

5. **代码审查与合并**
   ```bash
   git add .
   git commit -m "feat: Add SDK Cancellation Manager"
   git push origin feature/sdk-cancellation-manager
   ```

---

**下一步：** 开始 Phase 1 实施
