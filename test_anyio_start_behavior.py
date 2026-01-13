"""
测试 anyio TaskGroup.start() 的返回值行为

目的：验证 task_status.started() 是否可以传递返回值，
以及 TaskGroup.start() 是否会返回该值。
"""
import anyio
from anyio.abc import TaskStatus
import asyncio


async def test_started_with_value():
    """测试 started() 传递值的行为"""
    
    async def worker_with_value(task_status: TaskStatus) -> str:
        """测试：started() 传递值，wrapper 返回值"""
        print("Worker: 开始执行")
        await asyncio.sleep(0.1)
        
        # 传递值给 started()
        task_status.started("initialized_value")
        print("Worker: 已调用 started('initialized_value')")
        
        await asyncio.sleep(0.1)
        print("Worker: 准备返回 'final_result'")
        return "final_result"
    
    async with anyio.create_task_group() as tg:
        result = await tg.start(worker_with_value)
        print(f"TaskGroup.start() 返回值: {result!r}")
    
    print(f"最终结果: {result!r}")
    return result


async def test_started_without_value():
    """测试 started() 不传递值的行为"""
    
    async def worker_without_value(task_status: TaskStatus) -> str:
        """测试：started() 不传递值，wrapper 返回值"""
        print("Worker: 开始执行")
        await asyncio.sleep(0.1)
        
        # 不传递值给 started()
        task_status.started()
        print("Worker: 已调用 started()")
        
        await asyncio.sleep(0.1)
        print("Worker: 准备返回 'final_result'")
        return "final_result"
    
    async with anyio.create_task_group() as tg:
        result = await tg.start(worker_without_value)
        print(f"TaskGroup.start() 返回值: {result!r}")
    
    print(f"最终结果: {result!r}")
    return result


async def test_started_order():
    """测试 started() 调用时机对返回值的影响"""
    
    async def worker_early_started(task_status: TaskStatus) -> str:
        """测试：先调用 started()，后返回值"""
        print("Worker: 开始执行")
        task_status.started("early_signal")
        print("Worker: 已调用 started('early_signal')")
        
        await asyncio.sleep(0.1)
        print("Worker: 准备返回 'final_result'")
        return "final_result"
    
    async def worker_late_started(task_status: TaskStatus) -> str:
        """测试：先计算结果，后调用 started()"""
        print("Worker: 开始执行")
        await asyncio.sleep(0.1)
        result = "computed_result"
        print(f"Worker: 计算得到结果 '{result}'")
        
        task_status.started(result)
        print(f"Worker: 已调用 started('{result}')")
        return result
    
    async with anyio.create_task_group() as tg:
        result1 = await tg.start(worker_early_started)
        print(f"早期 started() - TaskGroup.start() 返回值: {result1!r}\n")
    
    async with anyio.create_task_group() as tg:
        result2 = await tg.start(worker_late_started)
        print(f"延迟 started() - TaskGroup.start() 返回值: {result2!r}\n")
    
    return result1, result2


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试 1: started() 传递值的行为")
    print("=" * 60)
    result1 = await test_started_with_value()
    
    print("\n" + "=" * 60)
    print("测试 2: started() 不传递值的行为")
    print("=" * 60)
    result2 = await test_started_without_value()
    
    print("\n" + "=" * 60)
    print("测试 3: started() 调用时机的影响")
    print("=" * 60)
    result3 = await test_started_order()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print(f"测试 1 (传递值):     {result1!r}")
    print(f"测试 2 (不传递值):   {result2!r}")
    print(f"测试 3 (早期/延迟): {result3!r}")


if __name__ == "__main__":
    anyio.run(main)
