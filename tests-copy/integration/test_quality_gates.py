"""
Integration tests for quality gates workflow.

Tests the complete workflow of quality gates integration including:
- Epic processing with quality gate tracking
- Integration with existing SM-Dev-QA workflow
- Database integrity across operations
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil
import sqlite3

from autoBMAD.epic_automation.state_manager import StateManager


class TestQualityGatesIntegration:
    """Integration tests for quality gates workflow."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_progress.db"

        sm = StateManager(str(db_path))

        yield {
            "state_manager": sm,
            "db_path": db_path,
            "temp_dir": temp_dir
        }

        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def epic_id(self):
        """Sample epic ID."""
        return "docs/epics/epic-bmad-automation.md"

    @pytest.mark.asyncio
    async def test_complete_workflow_with_quality_tracking(self, temp_db, epic_id):
        """
        Test complete workflow from story processing through quality gates.

        This simulates the full lifecycle:
        1. Story status update
        2. Quality phase tracking
        3. Test automation tracking
        4. Status updates through the workflow
        """
        sm = temp_db["state_manager"]

        # Step 1: Create initial story record
        story_path = "docs/stories/001.extend-state-management.md"
        await sm.update_story_status(
            story_path=story_path,
            status="in_progress",
            phase="dev",
            iteration=1,
            epic_path=epic_id
        )

        # Verify story was created
        story = await sm.get_story_status(story_path)
        assert story is not None
        assert story["status"] == "in_progress"
        assert story["phase"] == "dev"

        # Step 2: Add quality phase records for multiple files
        quality_records = []
        test_files = [
            ("src/module1.py", 3, "Type errors", "Import unused"),
            ("src/module2.py", 1, "Missing type annotation", ""),
            ("tests/test_suite.py", 0, "", "All good"),
        ]

        for file_path, error_count, bp_errors, ruff_errors in test_files:
            record_id = await sm.add_quality_phase_record(
                epic_id=epic_id,
                file_path=file_path,
                error_count=error_count,
                basedpyright_errors=bp_errors,
                ruff_errors=ruff_errors,
                fix_status="pending" if error_count > 0 else "completed"
            )
            quality_records.append(record_id)

        # Step 3: Add test automation records
        test_records = []
        test_files_info = [
            ("tests/unit/test_module1.py", 2, "2 failing tests"),
            ("tests/integration/test_workflow.py", 1, "1 failing test"),
            ("tests/e2e/test_complete.py", 0, "All passing"),
        ]

        for test_path, failure_count, debug_info in test_files_info:
            record_id = await sm.add_test_phase_record(
                epic_id=epic_id,
                test_file_path=test_path,
                failure_count=failure_count,
                debug_info=debug_info,
                fix_status="pending" if failure_count > 0 else "completed"
            )
            test_records.append(record_id)

        # Step 4: Update story status to dev_completed
        await sm.update_story_status(
            story_path=story_path,
            status="dev_completed",
            phase="qa",
            iteration=2,
            epic_path=epic_id
        )

        # Step 5: Verify all data is correctly stored
        story = await sm.get_story_status(story_path)
        assert story["status"] == "dev_completed"
        assert story["iteration"] == 2

        quality_records_data = await sm.get_quality_phase_records(epic_id)
        assert len(quality_records_data) == 3

        test_records_data = await sm.get_test_phase_records(epic_id)
        assert len(test_records_data) == 3

        # Step 6: Update quality records as fixes are applied
        await sm.update_quality_phase_status(
            record_id=quality_records[0],
            fix_status="in_progress",
            error_count=1
        )

        # Step 7: Update test records as fixes are applied
        await sm.update_test_phase_status(
            record_id=test_records[0],
            fix_status="in_progress",
            failure_count=1,
            debug_info="1 test still failing"
        )

        # Step 8: Final verification
        updated_quality = await sm.get_quality_phase_records(epic_id)
        # Verify the updated record by finding it in the list
        updated_record = next((r for r in updated_quality if r['record_id'] == quality_records[0]), None)
        assert updated_record is not None
        assert updated_record["fix_status"] == "in_progress"
        assert updated_record["error_count"] == 1

        updated_tests = await sm.get_test_phase_records(epic_id)
        # Verify the updated record by finding it in the list
        updated_record = next((r for r in updated_tests if r['record_id'] == test_records[0]), None)
        assert updated_record is not None
        assert updated_record["fix_status"] == "in_progress"
        assert updated_tests[0]["failure_count"] == 1

    @pytest.mark.asyncio
    async def test_multiple_epics_isolation(self, temp_db):
        """
        Test that data for different epics is properly isolated.

        Ensures that quality and test phase records don't leak between epics.
        """
        sm = temp_db["state_manager"]

        epic1 = "docs/epics/epic-001.md"
        epic2 = "docs/epics/epic-002.md"

        # Add records for epic 1
        await sm.add_quality_phase_record(
            epic_id=epic1,
            file_path="src/file1.py",
            error_count=5,
            basedpyright_errors="Error in epic1",
            ruff_errors="Ruff error epic1",
            fix_status="pending"
        )

        # Add records for epic 2
        await sm.add_quality_phase_record(
            epic_id=epic2,
            file_path="src/file2.py",
            error_count=10,
            basedpyright_errors="Error in epic2",
            ruff_errors="Ruff error epic2",
            fix_status="pending"
        )

        # Verify isolation
        epic1_records = await sm.get_quality_phase_records(epic1)
        epic2_records = await sm.get_quality_phase_records(epic2)

        assert len(epic1_records) == 1
        assert len(epic2_records) == 1

        assert epic1_records[0]["file_path"] == "src/file1.py"
        assert epic1_records[0]["error_count"] == 5

        assert epic2_records[0]["file_path"] == "src/file2.py"
        assert epic2_records[0]["error_count"] == 10

    @pytest.mark.asyncio
    async def test_integration_with_existing_story_workflow(self, temp_db, epic_id):
        """
        Test that quality gates integrate seamlessly with existing story workflow.

        Ensures backward compatibility and that existing code continues to work.
        """
        sm = temp_db["state_manager"]

        # Use existing story workflow methods
        story_path = "docs/stories/002.integrate-basedpyright-ruff.md"

        # Create story
        await sm.update_story_status(
            story_path=story_path,
            status="pending",
            phase="sm",
            epic_path=epic_id
        )

        # Update through different phases
        await sm.update_story_status(
            story_path=story_path,
            status="in_progress",
            phase="dev",
            iteration=1,
            epic_path=epic_id
        )

        await sm.update_story_status(
            story_path=story_path,
            status="qa_completed",
            phase="qa",
            iteration=2,
            epic_path=epic_id
        )

        # Add quality gates tracking
        quality_id = await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/integrated.py",
            error_count=0,
            basedpyright_errors="",
            ruff_errors="",
            fix_status="completed"
        )

        # Continue story workflow
        await sm.update_story_status(
            story_path=story_path,
            status="completed",
            phase="completed",
            iteration=3,
            epic_path=epic_id
        )

        # Verify all data is accessible
        story = await sm.get_story_status(story_path)
        assert story["status"] == "completed"
        assert story["iteration"] == 3

        quality_records = await sm.get_quality_phase_records(epic_id)
        assert len(quality_records) == 1
        assert quality_records[0]["record_id"] == quality_id

        # Verify existing methods still work
        all_stories = await sm.get_all_stories()
        assert len(all_stories) == 1
        assert all_stories[0]["story_path"] == story_path

        stories_by_status = await sm.get_stories_by_status("completed")
        assert len(stories_by_status) == 1

        stats = await sm.get_stats()
        assert "completed" in stats
        assert stats["completed"] == 1

    @pytest.mark.asyncio
    async def test_database_integrity_across_operations(self, temp_db, epic_id):
        """
        Test that database integrity is maintained across all operations.

        Verifies ACID properties and consistency.
        """
        sm = temp_db["state_manager"]

        # Create a story
        await sm.update_story_status(
            story_path="docs/stories/test.md",
            status="in_progress",
            epic_path=epic_id
        )

        # Add quality records
        quality_ids = []
        for i in range(5):
            record_id = await sm.add_quality_phase_record(
                epic_id=epic_id,
                file_path=f"src/file{i}.py",
                error_count=i,
                basedpyright_errors=f"Error {i}",
                ruff_errors=f"Ruff {i}",
                fix_status="pending"
            )
            quality_ids.append(record_id)

        # Add test records
        test_ids = []
        for i in range(3):
            record_id = await sm.add_test_phase_record(
                epic_id=epic_id,
                test_file_path=f"tests/test{i}.py",
                failure_count=i,
                debug_info=f"Debug {i}",
                fix_status="pending"
            )
            test_ids.append(record_id)

        # Verify counts
        quality_records = await sm.get_quality_phase_records(epic_id)
        test_records = await sm.get_test_phase_records(epic_id)

        assert len(quality_records) == 5
        assert len(test_records) == 3

        # Update some records
        for i, record_id in enumerate(quality_ids[:3]):
            await sm.update_quality_phase_status(
                record_id=record_id,
                fix_status="completed",
                error_count=0
            )

        # Verify updates
        updated_quality = await sm.get_quality_phase_records(epic_id)
        completed_count = sum(1 for r in updated_quality if r["fix_status"] == "completed")
        assert completed_count == 3

        # Verify database consistency by direct query
        conn = sqlite3.connect(temp_db["db_path"])
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM code_quality_phase")
        quality_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM test_automation_phase")
        test_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stories")
        story_count = cursor.fetchone()[0]

        conn.close()

        assert quality_count == 5
        assert test_count == 3
        assert story_count == 1

    @pytest.mark.asyncio
    async def test_error_recovery_and_rollback(self, temp_db, epic_id):
        """
        Test that system can recover from errors and maintain data consistency.

        Verifies that partial failures don't corrupt the database.
        """
        sm = temp_db["state_manager"]

        # Create initial data
        await sm.update_story_status(
            story_path="docs/stories/test.md",
            status="in_progress",
            epic_path=epic_id
        )

        valid_record_id = await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/valid.py",
            error_count=1,
            basedpyright_errors="Valid error",
            ruff_errors="Valid ruff",
            fix_status="pending"
        )

        # Attempt to update non-existent record (should fail gracefully)
        success = await sm.update_quality_phase_status(
            record_id="00000000-0000-0000-0000-000000000000",
            fix_status="completed"
        )

        assert success is False

        # Verify valid data is still intact
        records = await sm.get_quality_phase_records(epic_id)
        assert len(records) == 1
        assert records[0]["record_id"] == valid_record_id
        assert records[0]["fix_status"] == "pending"

        # Verify operations still work after error
        await sm.update_quality_phase_status(
            record_id=valid_record_id,
            fix_status="completed"
        )

        updated_records = await sm.get_quality_phase_records(epic_id)
        assert updated_records[0]["fix_status"] == "completed"

    @pytest.mark.asyncio
    async def test_concurrent_quality_and_test_operations(self, temp_db, epic_id):
        """
        Test concurrent operations on quality and test phase records.

        Ensures thread-safety and proper locking.
        """
        sm = temp_db["state_manager"]

        # Create multiple concurrent quality records
        quality_tasks = []
        for i in range(5):
            task = sm.add_quality_phase_record(
                epic_id=epic_id,
                file_path=f"src/concurrent_{i}.py",
                error_count=i,
                basedpyright_errors=f"Error {i}",
                ruff_errors=f"Ruff {i}",
                fix_status="pending"
            )
            quality_tasks.append(task)

        # Create multiple concurrent test records
        test_tasks = []
        for i in range(5):
            task = sm.add_test_phase_record(
                epic_id=epic_id,
                test_file_path=f"tests/concurrent_{i}.py",
                failure_count=i,
                debug_info=f"Debug {i}",
                fix_status="pending"
            )
            test_tasks.append(task)

        # Wait for all operations to complete
        quality_ids = await asyncio.gather(*quality_tasks)
        test_ids = await asyncio.gather(*test_tasks)

        # Verify all records were created
        assert len(quality_ids) == 5
        assert len(test_ids) == 5

        # Verify all records are in database
        quality_records = await sm.get_quality_phase_records(epic_id)
        test_records = await sm.get_test_phase_records(epic_id)

        assert len(quality_records) == 5
        assert len(test_records) == 5

    @pytest.mark.asyncio
    async def test_workflow_progress_tracking(self, temp_db, epic_id):
        """
        Test that workflow progress can be tracked through quality gates.

        Verifies that the quality gates can be used to track overall progress.
        """
        sm = temp_db["state_manager"]

        story_path = "docs/stories/progress_tracking.md"

        # Start story
        await sm.update_story_status(
            story_path=story_path,
            status="in_progress",
            phase="dev",
            epic_path=epic_id
        )

        # Add initial quality check (many errors)
        await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/module.py",
            error_count=10,
            basedpyright_errors="10 type errors",
            ruff_errors="10 style issues",
            fix_status="pending"
        )

        # Simulate progress: some errors fixed
        await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/module.py",
            error_count=5,
            basedpyright_errors="5 type errors remaining",
            ruff_errors="5 style issues fixed",
            fix_status="in_progress"
        )

        # Simulate more progress: most errors fixed
        await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/module.py",
            error_count=2,
            basedpyright_errors="2 type errors remaining",
            ruff_errors="All style issues fixed",
            fix_status="in_progress"
        )

        # Final state: all errors fixed
        await sm.add_quality_phase_record(
            epic_id=epic_id,
            file_path="src/module.py",
            error_count=0,
            basedpyright_errors="All type errors fixed",
            ruff_errors="All style issues fixed",
            fix_status="completed"
        )

        # Get all quality records for this file
        quality_records = await sm.get_quality_phase_records(epic_id)

        # Verify we can track the progress
        assert len(quality_records) == 4

        # Verify that we have records with all expected error counts and statuses
        error_counts = {r["error_count"] for r in quality_records}
        fix_statuses = {r["fix_status"] for r in quality_records}

        assert error_counts == {0, 2, 5, 10}
        assert fix_statuses == {"pending", "in_progress", "completed"}

        # Find and verify the completed record (all errors fixed)
        completed_records = [r for r in quality_records if r["fix_status"] == "completed"]
        assert len(completed_records) == 1
        assert completed_records[0]["error_count"] == 0
        assert "All type errors fixed" in completed_records[0]["basedpyright_errors"]
        assert "All style issues fixed" in completed_records[0]["ruff_errors"]

        # Find and verify the initial record (many errors)
        pending_records = [r for r in quality_records if r["fix_status"] == "pending"]
        assert len(pending_records) == 1
        assert pending_records[0]["error_count"] == 10
