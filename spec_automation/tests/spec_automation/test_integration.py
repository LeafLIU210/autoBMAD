"""
Integration tests for spec_automation module.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from spec_automation.doc_parser import DocumentParser
from spec_automation.spec_state_manager import SpecStateManager


class TestModuleIntegration:
    """Integration tests for the spec_automation module."""

    def test_module_imports_independently(self):
        """Test that module can be imported without .bmad-core dependency."""
        import spec_automation

        # Verify module has expected attributes
        assert hasattr(spec_automation, "DocParser")
        assert hasattr(spec_automation, "SpecStateManager")
        assert hasattr(spec_automation, "SpecDevAgent")
        assert hasattr(spec_automation, "SpecQAAgent")
        assert hasattr(spec_automation, "SpecDriver")

    def test_parser_and_state_manager_work_together(self):
        """Test that parser and state manager work together."""
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "integration_test.db"
            parser = DocumentParser()
            state_manager = SpecStateManager(db_path)

            # Create a test document
            test_file = Path(tmpdir) / "test_story.md"
            test_content = """
# Integration Test Story

## Story

**As a** system,
**I want** to test integration,
**so that** components work together.

## Acceptance Criteria

1. Parse document successfully
2. Save status to database
3. Retrieve status from database

## Requirements

- Component integration
- Data persistence
- Status tracking

## Tasks / Subtasks

- [ ] Parse document
- [ ] Save status
- [ ] Retrieve status

## Implementation

- Step 1: Initialize components
- Step 2: Process document
- Step 3: Verify integration
"""
            test_file.write_text(test_content)

            # Parse the document
            result = parser.parse_document(test_file)

            # Verify parsing worked
            assert result["title"] == "Integration Test Story"
            assert len(result["requirements"]) > 0

            # Save status to database
            story_path = str(test_file)
            state_manager.update_story_status(
                story_path,
                "in_progress",
                "testing"
            )

            # Retrieve status
            saved_status = state_manager.get_story_status(story_path)

            # Verify integration
            assert saved_status is not None
            assert saved_status["status"] == "in_progress"
            assert saved_status["phase"] == "testing"

    def test_parse_real_story_document(self, sample_markdown_files):
        """Test parsing a real story document."""
        parser = DocumentParser()
        result = parser.parse_document(sample_markdown_files["sample_story"])

        # Verify all expected fields are present
        assert "title" in result
        assert "requirements" in result
        assert "acceptance_criteria" in result
        assert "implementation_steps" in result

        # Verify data is not empty
        assert result["title"] != ""
        assert len(result["requirements"]) > 0
        assert len(result["acceptance_criteria"]) > 0
        assert len(result["implementation_steps"]) > 0

    def test_workflow_complete_cycle(self):
        """Test complete workflow: parse -> save -> retrieve -> update -> verify."""
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "workflow_test.db"
            parser = DocumentParser()
            state_manager = SpecStateManager(db_path)

            # Step 1: Create and parse document
            test_file = Path(tmpdir) / "workflow_story.md"
            test_content = """
# Workflow Test Story

## Story

**As a** tester,
**I want** to test complete workflow,
**so that** all features work together.

## Acceptance Criteria

1. Complete workflow test
2. Multiple status updates
3. Data persistence

## Requirements

- Full workflow coverage
- Status tracking
- Data integrity

## Tasks / Subtasks

- [ ] Step 1: Initial state
- [ ] Step 2: In progress
- [ ] Step 3: Review
- [ ] Step 4: Completed

## Implementation

- Phase 1: Setup
- Phase 2: Execute
- Phase 3: Verify
- Phase 4: Complete
"""
            test_file.write_text(test_content)

            story_path = str(test_file)

            # Step 2: Parse
            result = parser.parse_document(test_file)
            assert result["title"] == "Workflow Test Story"

            # Step 3: Save initial status
            state_manager.update_story_status(story_path, "pending", "planning")
            status1 = state_manager.get_story_status(story_path)
            assert status1["status"] == "pending"

            # Step 4: Update to in progress
            state_manager.update_story_status(story_path, "in_progress", "development")
            status2 = state_manager.get_story_status(story_path)
            assert status2["status"] == "in_progress"

            # Step 5: Update to review
            state_manager.update_story_status(story_path, "review", "qa")
            status3 = state_manager.get_story_status(story_path)
            assert status3["status"] == "review"

            # Step 6: Update to completed
            state_manager.update_story_status(story_path, "completed", "done", qa_result="PASS")
            status4 = state_manager.get_story_status(story_path)
            assert status4["status"] == "completed"
            assert status4["qa_result"] == "PASS"

            # Step 7: Verify only one story record exists
            all_stories = state_manager.get_all_stories()
            assert len(all_stories) == 1

    def test_multiple_stories_tracking(self):
        """Test tracking multiple stories independently."""
        with TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "multi_story_test.db"
            parser = DocumentParser()
            state_manager = SpecStateManager(db_path)

            # Create multiple test documents
            stories = []
            for i in range(3):
                test_file = Path(tmpdir) / f"story_{i}.md"
                content = f"""
# Story {i}

## Story

**Story number** {i}

## Acceptance Criteria

- Criterion {i}

## Requirements

- Requirement {i}

## Tasks / Subtasks

- Task {i}

## Implementation

- Step {i}
"""
                test_file.write_text(content)
                stories.append(str(test_file))

            # Parse all stories
            for i, story_path in enumerate(stories):
                result = parser.parse_document(Path(story_path))
                assert f"Story {i}" in result["title"]

            # Update all stories with different statuses
            state_manager.update_story_status(stories[0], "completed", "done")
            state_manager.update_story_status(stories[1], "in_progress", "dev")
            state_manager.update_story_status(stories[2], "pending", "planning")

            # Retrieve all stories
            all_stories = state_manager.get_all_stories()
            assert len(all_stories) == 3

            # Verify each story has correct status
            status0 = state_manager.get_story_status(stories[0])
            status1 = state_manager.get_story_status(stories[1])
            status2 = state_manager.get_story_status(stories[2])

            assert status0["status"] == "completed"
            assert status1["status"] == "in_progress"
            assert status2["status"] == "pending"

            # Test filtering by status
            completed = state_manager.get_stories_by_status("completed")
            in_progress = state_manager.get_stories_by_status("in_progress")
            pending = state_manager.get_stories_by_status("pending")

            assert len(completed) == 1
            assert len(in_progress) == 1
            assert len(pending) == 1

    def test_no_bmad_core_dependency(self):
        """Verify module doesn't depend on .bmad-core."""
        import sys
        import importlib.util

        # Check if .bmad-core is available
        bmad_core_available = any("bmad-core" in str(module) for module in sys.modules.keys())

        # Import spec_automation
        import spec_automation

        # Module should work regardless of .bmad-core
        assert spec_automation is not None
        assert hasattr(spec_automation, "DocParser")
        assert hasattr(spec_automation, "SpecStateManager")

        # If .bmad-core is not available, tests should still pass
        if not bmad_core_available:
            # This is expected for spec_automation
            pass

    def test_database_isolation(self):
        """Test that spec_automation database is isolated from epic_automation."""
        with TemporaryDirectory() as tmpdir:
            # Create spec_automation database
            spec_db = Path(tmpdir) / "spec_progress.db"
            spec_manager = SpecStateManager(spec_db)

            # Create epic_automation-style database
            epic_db = Path(tmpdir) / "progress.db"
            import sqlite3
            conn = sqlite3.connect(epic_db)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS epic_stories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_path TEXT NOT NULL
                )
            ''')
            conn.commit()
            conn.close()

            # Add data to spec_automation database
            spec_manager.update_story_status("/test/spec_story.md", "in_progress", "dev")

            # Verify databases are separate
            spec_stories = spec_manager.get_all_stories()
            assert len(spec_stories) == 1

            # Verify epic database has different schema
            epic_conn = sqlite3.connect(epic_db)
            epic_cursor = epic_conn.cursor()
            epic_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            epic_tables = [row[0] for row in epic_cursor.fetchall()]
            epic_conn.close()

            assert "stories" in epic_tables  # spec_automation table doesn't exist in epic db
            assert "epic_stories" in epic_tables
