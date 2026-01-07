"""
性能测试脚本 - Performance Test

测试修复后的系统性能。
"""

import asyncio
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# 设置UTF-8编码输出
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 添加父目录到路径
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)


class PerformanceTester:
    """性能测试器"""

    def __init__(self):
        self.test_results = []
        self.baseline_metrics = {
            "sdk_session_creation_time": 0.5,  # 0.5秒
            "qa_review_time": 60.0,  # 60秒
            "state_update_time": 0.1,  # 0.1秒
            "error_rate": 0.05  # 5%
        }

    async def run_performance_tests(self) -> Dict[str, Any]:
        """运行性能测试"""
        print("=" * 80)
        print("Epic自动化系统性能测试")
        print("=" * 80)
        print()

        # 1. 测试SDK会话创建性能
        await self.test_sdk_session_creation()

        # 2. 测试QA审查性能
        await self.test_qa_review_performance()

        # 3. 测试状态更新性能
        await self.test_state_update_performance()

        # 4. 测试并发处理性能
        await self.test_concurrent_processing()

        # 5. 测试错误恢复性能
        await self.test_error_recovery()

        # 6. 生成性能报告
        return self.generate_performance_report()

    async def test_sdk_session_creation(self):
        """测试SDK会话创建性能"""
        print("1. 测试SDK会话创建性能...")

        try:
            from fixed_modules.sdk_session_manager_fixed import SDKSessionManager

            session_manager = SDKSessionManager()
            creation_times = []

            # 测试会话创建
            for i in range(10):
                start_time = time.time()

                async with session_manager.create_session(f"test_agent_{i}"):
                    await asyncio.sleep(0.01)  # 模拟会话使用

                end_time = time.time()
                creation_times.append(end_time - start_time)

            # 计算统计信息
            avg_time = statistics.mean(creation_times)
            min_time = min(creation_times)
            max_time = max(creation_times)

            print(f"   平均创建时间: {avg_time:.3f}秒")
            print(f"   最快创建时间: {min_time:.3f}秒")
            print(f"   最慢创建时间: {max_time:.3f}秒")

            # 评估性能
            if avg_time <= self.baseline_metrics["sdk_session_creation_time"]:
                print("   ✅ SDK会话创建性能良好")
                self.test_results.append({
                    "test": "SDK会话创建",
                    "status": "PASS",
                    "average_time": avg_time,
                    "baseline": self.baseline_metrics["sdk_session_creation_time"]
                })
            else:
                print("   ⚠️  SDK会话创建性能需要优化")
                self.test_results.append({
                    "test": "SDK会话创建",
                    "status": "WARN",
                    "average_time": avg_time,
                    "baseline": self.baseline_metrics["sdk_session_creation_time"]
                })

        except Exception as e:
            print(f"   ❌ SDK会话创建测试失败: {e}")
            self.test_results.append({
                "test": "SDK会话创建",
                "status": "FAIL",
                "error": str(e)
            })

        print()

    async def test_qa_review_performance(self):
        """测试QA审查性能"""
        print("2. 测试QA审查性能...")

        try:
            from fixed_modules.qa_agent_fixed import QAAgent

            qa_agent = QAAgent()

            # 模拟QA审查
            start_time = time.time()

            # 创建模拟故事内容
            story_content = """
# Test Story

## Status
Ready for Review

## Implementation
This is a test story for performance testing.
            """.strip()

            # 注意：实际QA审查会调用外部API，这里只是测试执行流程
            try:
                result = await qa_agent.execute(
                    story_content=story_content,
                    story_path="test_story.md",
                    max_retries=0  # 禁用重试以加快测试
                )

                end_time = time.time()
                review_time = end_time - start_time

                print(f"   QA审查时间: {review_time:.3f}秒")

                # 评估性能（QA审查通常需要较长时间，这里只测试流程）
                if review_time <= self.baseline_metrics["qa_review_time"]:
                    print("   ✅ QA审查性能良好")
                    self.test_results.append({
                        "test": "QA审查",
                        "status": "PASS",
                        "time": review_time,
                        "baseline": self.baseline_metrics["qa_review_time"]
                    })
                else:
                    print("   ⚠️  QA审查时间较长")
                    self.test_results.append({
                        "test": "QA审查",
                        "status": "WARN",
                        "time": review_time,
                        "baseline": self.baseline_metrics["qa_review_time"]
                    })

            except Exception as e:
                # QA审查可能因为外部依赖失败，这是预期的
                print(f"   ⚠️  QA审查测试遇到预期错误: {e}")
                self.test_results.append({
                    "test": "QA审查",
                    "status": "SKIP",
                    "reason": str(e)
                })

        except Exception as e:
            print(f"   ❌ QA审查测试失败: {e}")
            self.test_results.append({
                "test": "QA审查",
                "status": "FAIL",
                "error": str(e)
            })

        print()

    async def test_state_update_performance(self):
        """测试状态更新性能"""
        print("3. 测试状态更新性能...")

        try:
            from fixed_modules.state_manager_fixed import StateManager

            # 使用临时数据库
            state_manager = StateManager("test_progress.db")

            update_times = []

            # 测试状态更新
            for i in range(20):
                start_time = time.time()

                success, version = await state_manager.update_story_status(
                    story_path=f"test_story_{i}.md",
                    status="test_status",
                    phase="test_phase"
                )

                end_time = time.time()

                if success:
                    update_times.append(end_time - start_time)

            if update_times:
                avg_time = statistics.mean(update_times)
                min_time = min(update_times)
                max_time = max(update_times)

                print(f"   平均更新时间: {avg_time:.3f}秒")
                print(f"   最快更新时间: {min_time:.3f}秒")
                print(f"   最慢更新时间: {max_time:.3f}秒")

                # 评估性能
                if avg_time <= self.baseline_metrics["state_update_time"]:
                    print("   ✅ 状态更新性能良好")
                    self.test_results.append({
                        "test": "状态更新",
                        "status": "PASS",
                        "average_time": avg_time,
                        "baseline": self.baseline_metrics["state_update_time"]
                    })
                else:
                    print("   ⚠️  状态更新性能需要优化")
                    self.test_results.append({
                        "test": "状态更新",
                        "status": "WARN",
                        "average_time": avg_time,
                        "baseline": self.baseline_metrics["state_update_time"]
                    })
            else:
                print("   ❌ 没有成功的状态更新")
                self.test_results.append({
                    "test": "状态更新",
                    "status": "FAIL",
                    "error": "No successful updates"
                })

            # 清理测试数据库
            test_db = Path("test_progress.db")
            if test_db.exists():
                test_db.unlink()

        except Exception as e:
            print(f"   ❌ 状态更新测试失败: {e}")
            self.test_results.append({
                "test": "状态更新",
                "status": "FAIL",
                "error": str(e)
            })

        print()

    async def test_concurrent_processing(self):
        """测试并发处理性能"""
        print("4. 测试并发处理性能...")

        try:
            from fixed_modules.sdk_session_manager_fixed import SDKSessionManager

            session_manager = SDKSessionManager()
            results = []

            # 创建并发任务
            async def test_session(agent_id: int):
                start_time = time.time()

                async with session_manager.create_session(f"concurrent_agent_{agent_id}"):
                    await asyncio.sleep(0.05)  # 模拟工作

                end_time = time.time()
                return {
                    "agent_id": agent_id,
                    "duration": end_time - start_time,
                    "success": True
                }

            # 运行并发测试
            tasks = [test_session(i) for i in range(5)]
            start_time = time.time()

            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time = end_time - start_time

            # 分析结果
            successful_results = [r for r in results if r["success"]]
            durations = [r["duration"] for r in successful_results]

            if durations:
                avg_duration = statistics.mean(durations)
                print(f"   并发任务数: {len(tasks)}")
                print(f"   总执行时间: {total_time:.3f}秒")
                print(f"   平均任务时间: {avg_duration:.3f}秒")
                print(f"   成功任务数: {len(successful_results)}")

                # 评估并发性能
                if len(successful_results) == len(tasks):
                    print("   ✅ 并发处理性能良好")
                    self.test_results.append({
                        "test": "并发处理",
                        "status": "PASS",
                        "total_time": total_time,
                        "success_rate": len(successful_results) / len(tasks)
                    })
                else:
                    print("   ⚠️  部分并发任务失败")
                    self.test_results.append({
                        "test": "并发处理",
                        "status": "WARN",
                        "total_time": total_time,
                        "success_rate": len(successful_results) / len(tasks)
                    })
            else:
                print("   ❌ 没有成功的并发任务")
                self.test_results.append({
                    "test": "并发处理",
                    "status": "FAIL",
                    "error": "No successful tasks"
                })

        except Exception as e:
            print(f"   ❌ 并发处理测试失败: {e}")
            self.test_results.append({
                "test": "并发处理",
                "status": "FAIL",
                "error": str(e)
            })

        print()

    async def test_error_recovery(self):
        """测试错误恢复性能"""
        print("5. 测试错误恢复性能...")

        try:
            from fixed_modules.sdk_session_manager_fixed import SDKSessionManager

            session_manager = SDKSessionManager()

            # 创建会失败的SDK函数
            async def failing_sdk_func():
                await asyncio.sleep(0.01)
                raise RuntimeError("Test error")

            # 测试错误恢复
            start_time = time.time()

            result = await session_manager.execute_isolated(
                agent_name="test_error_recovery",
                sdk_func=failing_sdk_func,
                timeout=5.0,
                max_retries=2
            )

            end_time = time.time()
            recovery_time = end_time - start_time

            print(f"   错误恢复时间: {recovery_time:.3f}秒")
            print(f"   重试次数: {result.retry_count}")
            print(f"   执行结果: {'成功' if result.success else '失败'}")

            # 评估错误恢复性能
            if result.error_type.name in ["TIMEOUT", "SDK_ERROR"]:
                print("   ✅ 错误恢复机制正常工作")
                self.test_results.append({
                    "test": "错误恢复",
                    "status": "PASS",
                    "recovery_time": recovery_time,
                    "retry_count": result.retry_count
                })
            else:
                print("   ⚠️  错误恢复结果异常")
                self.test_results.append({
                    "test": "错误恢复",
                    "status": "WARN",
                    "recovery_time": recovery_time,
                    "retry_count": result.retry_count
                })

        except Exception as e:
            print(f"   ❌ 错误恢复测试失败: {e}")
            self.test_results.append({
                "test": "错误恢复",
                "status": "FAIL",
                "error": str(e)
            })

        print()

    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        # 计算总体性能分数
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        warn_tests = len([r for r in self.test_results if r["status"] == "WARN"])

        performance_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "timestamp": time.time(),
            "performance_score": performance_score,
            "test_summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warn_tests
            },
            "test_results": self.test_results,
            "baseline_metrics": self.baseline_metrics,
            "recommendations": []
        }

        # 生成建议
        if failed_tests > 0:
            report["recommendations"].append("修复失败的测试以提高系统稳定性")

        if warn_tests > 0:
            report["recommendations"].append("优化警告项以提高系统性能")

        if performance_score >= 90:
            report["overall_status"] = "EXCELLENT"
        elif performance_score >= 70:
            report["overall_status"] = "GOOD"
        elif performance_score >= 50:
            report["overall_status"] = "FAIR"
        else:
            report["overall_status"] = "POOR"

        # 保存报告
        report_file = Path("performance_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 打印摘要
        print("=" * 80)
        print("性能测试摘要")
        print("=" * 80)
        print(f"性能分数: {performance_score:.1f}%")
        print(f"总体状态: {report['overall_status']}")
        print(f"通过测试: {passed_tests}/{total_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"警告测试: {warn_tests}")
        print()

        if report["recommendations"]:
            print("建议:")
            for recommendation in report["recommendations"]:
                print(f"  • {recommendation}")
            print()

        print(f"详细报告已保存到: {report_file}")
        print("=" * 80)

        return report


async def main():
    """主函数"""
    tester = PerformanceTester()
    report = await tester.run_performance_tests()

    # 根据性能结果设置退出码
    if report["overall_status"] in ["EXCELLENT", "GOOD"]:
        print("\n[PASS] System performance is good!")
        sys.exit(0)
    elif report["overall_status"] == "FAIR":
        print("\n[WARNING] System performance is fair, optimization recommended")
        sys.exit(1)
    else:
        print("\n[FAIL] System performance is poor, fixes needed")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
