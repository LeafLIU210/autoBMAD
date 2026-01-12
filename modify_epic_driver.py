#!/usr/bin/env python3
"""
修改EpicDriver以使用控制器层
"""

import re

# 读取文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改导入部分
old_import = '''from autoBMAD.epic_automation.state_manager import (
                StateManager,  # type: ignore
            )

            self.sm_agent = SMAgent()
            self.dev_agent = DevAgent(use_claude=use_claude)
            self.qa_agent = QAAgent()
            self.state_manager = StateManager()'''

new_import = '''from autoBMAD.epic_automation.state_manager import (
                StateManager,  # type: ignore
            )
            from autoBMAD.epic_automation.controllers.sm_controller import SMController  # type: ignore
            from autoBMAD.epic_automation.controllers.devqa_controller import DevQaController  # type: ignore
            from autoBMAD.epic_automation.controllers.quality_controller import QualityController  # type: ignore

            # Create agents (for potential direct access)
            self.sm_agent = SMAgent()
            self.dev_agent = DevAgent(use_claude=use_claude)
            self.qa_agent = QAAgent()
            self.state_manager = StateManager()

            # Create controllers (main interface)
            self.sm_controller = None  # Will be created per story in async context
            self.devqa_controller = None  # Will be created per story in async context
            self.quality_controller = None  # Will be created when needed'''

content = content.replace(old_import, new_import)

# 修改 execute_sm_phase 方法
old_sm_phase = '''    async def execute_sm_phase(self, story_path: str) -> bool:
        """Execute SM (Story Master) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing SM phase for {story_path}")

        try:
            # Read story content
            with open(story_path, encoding="utf-8") as f:
                story_content = f.read()

            # Execute SM phase with story_path parameter
            result: bool = await self.sm_agent.execute(story_content, story_path)

            # Update state
            state_update_success = await self.state_manager.update_story_status(
                story_path=story_path, status="sm_completed", phase="sm"
            )

            if not state_update_success:
                logger.warning(
                    f"State update failed for {story_path} but business logic completed, "
                    f"continuing with sm_completed status"
                )

            logger.info(f"SM phase completed for {story_path}")
            return result

        except Exception as e:
            logger.error(f"SM phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e)
            )
            return False'''

new_sm_phase = '''    async def execute_sm_phase(self, story_path: str) -> bool:
        """Execute SM (Story Master) phase for a story.

        Args:
            story_path: Path to the story markdown file

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Executing SM phase for {story_path}")

        try:
            # Create SMController in async context
            import anyio
            async with anyio.create_task_group() as tg:
                # Read story content
                with open(story_path, encoding="utf-8") as f:
                    story_content = f.read()

                # Create SMController with task group
                from autoBMAD.epic_automation.controllers.sm_controller import SMController
                sm_controller = SMController(tg, project_root=Path.cwd())
                self.sm_controller = sm_controller

                # Execute SM phase
                result: bool = await sm_controller.execute(
                    epic_content=story_content,
                    story_id=Path(story_path).stem
                )

                # Update state
                state_update_success = await self.state_manager.update_story_status(
                    story_path=story_path, status="sm_completed", phase="sm"
                )

                if not state_update_success:
                    logger.warning(
                        f"State update failed for {story_path} but business logic completed, "
                        f"continuing with sm_completed status"
                    )

                logger.info(f"SM phase completed for {story_path}")
                return result

        except Exception as e:
            logger.error(f"SM phase failed for {story_path}: {e}")
            await self.state_manager.update_story_status(
                story_path=story_path, status="error", error=str(e)
            )
            return False'''

content = content.replace(old_sm_phase, new_sm_phase)

# 写入修改后的文件
with open('d:\\GITHUB\\pytQt_template\\autoBMAD/epic_automation/epic_driver.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("EpicDriver modified successfully!")
