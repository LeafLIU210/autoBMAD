#!/usr/bin/env python3
"""
修改EpicDriver的状态机逻辑，委托给DevQaController
"""

import re

# 读取文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 简化 _execute_story_processing 方法 - 委托给DevQaController
old_state_machine = '''    async def _execute_story_processing(self, story: "dict[str, Any]") -> bool:
        """
        Core story processing logic - driven purely by core status values.

        Dev-QA 循环完全由核心状态值驱动，不依赖 SDK 返回值。
        """
        story_path = story["path"]
        story_id = story["id"]

        try:
            # 检查是否已完成
            existing_status: dict[str, Any] = await self.state_manager.get_story_status(
                story_path
            )
            if existing_status and existing_status.get("status") in ["completed", "qa_waived"]:
                logger.info(f"Story already processed: {story_path} (status: {existing_status.get('status')})")
                return True

            # 🎯 核心改动：循环由核心状态值驱动
            iteration = 1
            max_dev_qa_cycles = 10

            while iteration <= max_dev_qa_cycles:
                logger.info(
                    f"[Epic Driver] Dev-QA cycle #{iteration} for {story_path}"
                )

                try:
                    # 1️⃣ 读取当前核心状态值
                    current_status = await self._parse_story_status(story_path)
                    logger.info(f"[Cycle {iteration}] Current status: {current_status}")

                except asyncio.CancelledError:
                    # 🎯 关键修复：SDK 内部取消后的延迟 CancelledError
                    # 完全封装，不影响工作流
                    logger.warning(
                        f"[Cycle {iteration}] SDK cleanup triggered CancelledError (non-fatal), "
                        f"using last known status or fallback"
                    )
                    # 使用 fallback 解析状态
                    current_status = self._parse_story_status_fallback(story_path)
                    logger.info(f"[Cycle {iteration}] Fallback status: {current_status}")

                # 🎯 关键修复：状态解析后等待 SDK 清理完成，避免连续 SDK 调用
                # 增加等待时间到 2 秒，确保 cancel scope 完全清理
                # 将 sleep 单独放在 try-except 外面，吸收所有延迟的 CancelledError
                try:
                    logger.debug(f"[Cycle {iteration}] Waiting for SDK cleanup (2 seconds)...")
                    await asyncio.sleep(2.0)
                except asyncio.CancelledError:
                    logger.debug(f"[Cycle {iteration}] CancelledError during sleep absorbed (non-fatal)")
                    # 完全吸收此 CancelledError，不再传播

                # 2️⃣ 根据核心状态值决定下一步
                if current_status in ["Done", "Ready for Done"]:
                    # ✅ 终态：故事完成
                    logger.info(f"Story {story_id} completed (Status: {current_status})")
                    return True

                elif current_status in ["Draft", "Ready for Development"]:
                    # 需要开发
                    logger.info(f"[Cycle {iteration}] Executing Dev phase (status: {current_status})")
                    await self.execute_dev_phase(story_path, iteration)
                    # ⚠️ 不检查返回值，继续循环

                elif current_status == "In Progress":
                    # 继续开发
                    logger.info(f"[Cycle {iteration}] Continuing Dev phase (status: {current_status})")
                    await self.execute_dev_phase(story_path, iteration)

                elif current_status == "Ready for Review":
                    # 需要 QA
                    logger.info(f"[Cycle {iteration}] Executing QA phase (status: {current_status})")
                    await self.execute_qa_phase(story_path)
                    # ⚠️ 不检查返回值，继续循环

                elif current_status == "Failed":
                    # 失败状态，尝试重新开发
                    logger.warning(f"[Cycle {iteration}] Story in failed state, retrying Dev phase")
                    await self.execute_dev_phase(story_path, iteration)

                else:
                    # 未知状态，尝试开发
                    logger.warning(f"[Cycle {iteration}] Unknown status '{current_status}', attempting Dev phase")
                    await self.execute_dev_phase(story_path, iteration)

                # 3️⃣ 等待 SDK 清理 + 状态更新
                await asyncio.sleep(1.0)

                # 4️⃣ 增加迭代计数
                iteration += 1

            # 超过最大循环次数
            logger.warning(
                f"Reached maximum Dev-QA cycles ({max_dev_qa_cycles}) for {story_path}"
            )
            return False

        except Exception as e:
            logger.error(f"Failed to process story {story_path}: {e}")'''

new_state_machine = '''    async def _execute_story_processing(self, story: "dict[str, Any]") -> bool:
        """
        Core story processing logic - now delegated to DevQaController.

        Dev-QA 循环委托给 DevQaController 管理，EpicDriver 负责整体编排。
        """
        story_path = story["path"]
        story_id = story["id"]

        try:
            # 检查是否已完成
            existing_status: dict[str, Any] = await self.state_manager.get_story_status(
                story_path
            )
            if existing_status and existing_status.get("status") in ["completed", "qa_waived"]:
                logger.info(f"Story already processed: {story_path} (status: {existing_status.get('status')})")
                return True

            logger.info(f"[Epic Driver] Starting Dev-QA pipeline for {story_path}")

            # 🎯 核心改动：委托给 DevQaController 管理完整状态机
            import anyio
            async with anyio.create_task_group() as tg:
                # Create DevQaController with task group
                from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
                devqa_controller = DevQaController(
                    tg,
                    use_claude=self.use_claude,
                    log_manager=self.log_manager
                )
                self.devqa_controller = devqa_controller

                # Execute complete Dev-QA pipeline using the controller
                # DevQaController manages all state transitions internally
                result: bool = await devqa_controller.run_pipeline(
                    story_path,
                    max_rounds=self.max_iterations
                )

                if result:
                    logger.info(f"Story {story_id} completed successfully")
                    return True
                else:
                    logger.warning(f"Story {story_id} did not complete within max rounds")
                    return False

        except Exception as e:
            logger.error(f"Failed to process story {story_path}: {e}")'''

content = content.replace(old_state_machine, new_state_machine)

# 写入修改后的文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("State machine logic simplified successfully!")
