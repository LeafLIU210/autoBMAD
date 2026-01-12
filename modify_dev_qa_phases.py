#!/usr/bin/env python3
"""
修改EpicDriver的Dev-QA阶段使用DevQaController
"""

import re

# 读取文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改 execute_dev_phase 方法 - 使用DevQaController
old_dev_phase = '''    async def execute_dev_phase(self, story_path: str, iteration: int = 1) -> bool:
        """
        Execute Dev (Development) phase for a story.

        Args:
            story_path: Path to the story markdown file
            iteration: Current iteration count (for safety)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing Dev phase for {story_path} (iteration {iteration})")

        # Safety guard against infinite loops
        if iteration > self.max_iterations:
            logger.error(
                f"Max iterations ({self.max_iterations}) reached for {story_path}"
            )
            await self.state_manager.update_story_status(
                story_path=story_path, status="failed", error="Max iterations exceeded"
            )
            return False

        try:
            # Read story content
            with open(story_path, encoding="utf-8") as f:
                _ = f.read()

            # Set log_manager to dev_agent for SDK logging
            self.dev_agent._log_manager = self.log_manager

            # Execute Dev phase with story_path parameter
            result: bool = await self.dev_agent.execute(story_path)

            # Update state
            state_update_success = await self.state_manager.update_story_status(
                story_path=story_path,
                status="completed",  # 从 "dev_completed" 更新为 "completed"
                phase="dev",
                iteration=iteration,
            )

            if not state_update_success:
                logger.warning(
                    f"State update failed for {story_path} but business logic completed, "
                    f"continuing with dev_completed status"
                )

            logger.info(f"Dev phase completed for {story_path}")
            return result

        except Exception as e:
            logger.error(f"Dev phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e)
            )
            return False'''

new_dev_phase = '''    async def execute_dev_phase(self, story_path: str, iteration: int = 1) -> bool:
        """
        Execute Dev (Development) phase for a story using DevQaController.

        Args:
            story_path: Path to the story markdown file
            iteration: Current iteration count (for safety)

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing Dev phase for {story_path} (iteration {iteration})")

        # Safety guard against infinite loops
        if iteration > self.max_iterations:
            logger.error(
                f"Max iterations ({self.max_iterations}) reached for {story_path}"
            )
            await self.state_manager.update_story_status(
                story_path=story_path, status="failed", error="Max iterations exceeded"
            )
            return False

        try:
            # Create DevQaController in async context
            import anyio
            async with anyio.create_task_group() as tg:
                # Set log_manager for agents
                # (handled within DevQaController)

                # Create DevQaController with task group
                from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController
                devqa_controller = DevQaController(
                    tg,
                    use_claude=self.use_claude,
                    log_manager=self.log_manager
                )
                self.devqa_controller = devqa_controller

                # Execute Dev-QA pipeline using the controller
                result: bool = await devqa_controller.execute(story_path)

                # Update state
                state_update_success = await self.state_manager.update_story_status(
                    story_path=story_path,
                    status="completed",  # 从 "dev_completed" 更新为 "completed"
                    phase="dev",
                    iteration=iteration,
                )

                if not state_update_success:
                    logger.warning(
                        f"State update failed for {story_path} but business logic completed, "
                        f"continuing with dev_completed status"
                    )

                logger.info(f"Dev phase completed for {story_path}")
                return result

        except Exception as e:
            logger.error(f"Dev phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e)
            )
            return False'''

content = content.replace(old_dev_phase, new_dev_phase)

# 删除 execute_qa_phase 方法（现在由DevQaController处理）
old_qa_phase = '''    async def execute_qa_phase(self, story_path: str) -> bool:
        """
        Execute QA (Quality Assurance) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if QA passes, False otherwise
        """
        logger.info(f"Executing QA phase for {story_path}")

        try:
            # Read story content
            with open(story_path, encoding="utf-8") as f:
                _ = f.read()

            # Execute QA phase with tools integration
            qa_result: dict[str, Any] = await self.qa_agent.execute(
                story_path=story_path,
            )

            # QA phase completed - no intermediate qa_completed state set
            # QA agent re-evaluates story document status via SDK

            if qa_result.get("passed", False):
                logger.info(f"QA phase passed for {story_path}")
                completion_state_update_success = (
                    await self.state_manager.update_story_status(
                        story_path=story_path, status="completed"
                    )
                )

                if not completion_state_update_success:
                    logger.warning(
                        f"Completion state update failed for {story_path} but QA passed successfully"
                    )
                return True
            else:
                logger.info(f"QA phase failed for {story_path}, setting in_progress")
                await self.state_manager.update_story_status(
                    story_path=story_path, status="in_progress"
                )

                return True

        except Exception as e:
            logger.error(f"QA phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e)
            )
            return False'''

new_qa_phase = '''    async def execute_qa_phase(self, story_path: str) -> bool:
        """
        Execute QA (Quality Assurance) phase for a story.

        Note: This method is now deprecated. QA is handled by DevQaController
        in the execute_dev_phase method.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if QA passes, False otherwise
        """
        logger.warning(
            f"execute_qa_phase is deprecated. QA is now handled by DevQaController. "
            f"Use execute_dev_phase which manages the complete Dev-QA cycle."
        )
        return True  # No-op - QA is handled in DevQaController'''

content = content.replace(old_qa_phase, new_qa_phase)

# 写入修改后的文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Dev-QA phases modified successfully!")
