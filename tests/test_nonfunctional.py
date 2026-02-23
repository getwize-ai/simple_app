"""
Non-functional tests for the Simple Todo Application.

Covers:
  REQ-NF-006  Persist todo items to JSON so data survives restart
  REQ-NF-007  Validate titles: not empty, max 200 characters
  REQ-NF-008  All CRUD operations complete within 100 milliseconds
  REQ-NF-009  Proper error handling with descriptive error messages
  REQ-NF-010  Command-line interface with clear menu options
"""

import json
import time
import pytest
from pathlib import Path
from io import StringIO
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import TodoApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app(tmp_path, monkeypatch):
    """Return a fresh TodoApp backed by a temporary data file."""
    monkeypatch.chdir(tmp_path)
    return TodoApp()


@pytest.fixture
def app_with_todos(app):
    app.create_todo("Buy groceries", "Milk, eggs, bread")
    app.create_todo("Write report")
    app.create_todo("Call dentist")
    return app


# ---------------------------------------------------------------------------
# REQ-NF-006  JSON persistence
# ---------------------------------------------------------------------------

class TestPersistence:
    """REQ-NF-006: The application shall persist all todo items to a JSON file
    so that data remains available after application restart."""

    def test_todos_saved_to_json_file(self, app, tmp_path):
        app.create_todo("Persistent task")
        data_file = tmp_path / "todos.json"
        assert data_file.exists()

    def test_json_file_contains_valid_json(self, app, tmp_path):
        app.create_todo("Check JSON")
        data_file = tmp_path / "todos.json"
        content = json.loads(data_file.read_text())
        assert isinstance(content, list)

    def test_data_survives_restart(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        app1 = TodoApp()
        app1.create_todo("Survives restart", "Important")

        app2 = TodoApp()
        assert len(app2.todos) == 1
        assert app2.todos[0]["title"] == "Survives restart"

    def test_multiple_todos_all_persisted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        app1 = TodoApp()
        for i in range(5):
            app1.create_todo(f"Todo {i}")

        app2 = TodoApp()
        assert len(app2.todos) == 5

    def test_completed_status_persisted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        app1 = TodoApp()
        app1.create_todo("Task to complete")
        app1.mark_complete(1)

        app2 = TodoApp()
        assert app2.todos[0]["completed"] is True

    def test_deletion_persisted_across_restart(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        app1 = TodoApp()
        app1.create_todo("Will be deleted")
        app1.create_todo("Will stay")
        app1.delete_todo(1)

        app2 = TodoApp()
        assert len(app2.todos) == 1
        assert app2.todos[0]["title"] == "Will stay"

    def test_edit_persisted_across_restart(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        app1 = TodoApp()
        app1.create_todo("Original title")
        app1.edit_todo(1, title="Edited title")

        app2 = TodoApp()
        assert app2.todos[0]["title"] == "Edited title"


# ---------------------------------------------------------------------------
# REQ-NF-007  Input validation
# ---------------------------------------------------------------------------

class TestValidation:
    """REQ-NF-007: The application shall validate that todo titles are not
    empty and are no longer than 200 characters."""

    def test_empty_title_rejected(self, app):
        result = app.create_todo("")
        assert result is False
        assert len(app.todos) == 0

    def test_whitespace_only_title_rejected(self, app):
        result = app.create_todo("   ")
        assert result is False
        assert len(app.todos) == 0

    def test_title_at_max_length_accepted(self, app):
        title = "A" * 200
        result = app.create_todo(title)
        assert result is True

    def test_title_exceeding_max_length_rejected(self, app):
        title = "A" * 201
        result = app.create_todo(title)
        assert result is False
        assert len(app.todos) == 0

    def test_valid_title_accepted(self, app):
        result = app.create_todo("Valid title")
        assert result is True

    def test_edit_with_empty_title_rejected(self, app_with_todos):
        result = app_with_todos.edit_todo(1, title="")
        assert result is False
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["title"] == "Buy groceries"  # unchanged

    def test_edit_with_too_long_title_rejected(self, app_with_todos):
        result = app_with_todos.edit_todo(1, title="X" * 201)
        assert result is False

    def test_validation_error_message_shown(self, app, capsys):
        app.create_todo("")
        output = capsys.readouterr().out
        assert "Error" in output or "empty" in output.lower() or "❌" in output


# ---------------------------------------------------------------------------
# REQ-NF-008  Performance — all CRUD operations under 100 ms
# ---------------------------------------------------------------------------

class TestPerformance:
    """REQ-NF-008: The application shall complete all todo operations
    (create, read, update, delete) within 100 milliseconds."""

    LIMIT_MS = 100

    def test_create_todo_within_100ms(self, app):
        start = time.perf_counter()
        app.create_todo("Speed test")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < self.LIMIT_MS, f"create_todo took {elapsed_ms:.1f} ms"

    def test_list_todos_within_100ms(self, app_with_todos, capsys):
        start = time.perf_counter()
        app_with_todos.list_todos()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < self.LIMIT_MS, f"list_todos took {elapsed_ms:.1f} ms"

    def test_mark_complete_within_100ms(self, app_with_todos):
        start = time.perf_counter()
        app_with_todos.mark_complete(1)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < self.LIMIT_MS, f"mark_complete took {elapsed_ms:.1f} ms"

    def test_edit_todo_within_100ms(self, app_with_todos):
        start = time.perf_counter()
        app_with_todos.edit_todo(1, title="Faster now")
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < self.LIMIT_MS, f"edit_todo took {elapsed_ms:.1f} ms"

    def test_delete_todo_within_100ms(self, app_with_todos):
        start = time.perf_counter()
        app_with_todos.delete_todo(1)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < self.LIMIT_MS, f"delete_todo took {elapsed_ms:.1f} ms"


# ---------------------------------------------------------------------------
# REQ-NF-009  Error handling with descriptive messages
# ---------------------------------------------------------------------------

class TestErrorHandling:
    """REQ-NF-009: The application shall implement proper error handling with
    descriptive error messages for all operations."""

    def test_create_with_empty_title_shows_error_message(self, app, capsys):
        app.create_todo("")
        output = capsys.readouterr().out
        assert len(output.strip()) > 0  # some message printed

    def test_mark_complete_unknown_id_shows_error(self, app_with_todos, capsys):
        app_with_todos.mark_complete(999)
        output = capsys.readouterr().out
        assert "999" in output or "not found" in output.lower() or "Error" in output

    def test_delete_unknown_id_shows_error(self, app_with_todos, capsys):
        app_with_todos.delete_todo(999)
        output = capsys.readouterr().out
        assert "999" in output or "not found" in output.lower() or "Error" in output

    def test_edit_unknown_id_shows_error(self, app_with_todos, capsys):
        app_with_todos.edit_todo(999, title="Ghost")
        output = capsys.readouterr().out
        assert "999" in output or "not found" in output.lower() or "Error" in output

    def test_create_too_long_title_shows_error(self, app, capsys):
        app.create_todo("X" * 201)
        output = capsys.readouterr().out
        assert "200" in output or "exceed" in output.lower() or "Error" in output

    def test_successful_create_shows_confirmation(self, app, capsys):
        app.create_todo("Success task")
        output = capsys.readouterr().out
        assert "Success task" in output or "created" in output.lower() or "✅" in output

    def test_successful_delete_shows_confirmation(self, app_with_todos, capsys):
        app_with_todos.delete_todo(1)
        output = capsys.readouterr().out
        assert "deleted" in output.lower() or "✅" in output

    def test_successful_edit_shows_confirmation(self, app_with_todos, capsys):
        app_with_todos.edit_todo(1, title="New name")
        output = capsys.readouterr().out
        assert "updated" in output.lower() or "✅" in output

    def test_corrupted_json_handled_gracefully(self, tmp_path, monkeypatch, capsys):
        """REQ-NF-009: corrupt data file must not crash the app."""
        monkeypatch.chdir(tmp_path)
        data_file = tmp_path / "todos.json"
        data_file.write_text("{invalid json}")

        app = TodoApp()  # should not raise
        assert app.todos == []


# ---------------------------------------------------------------------------
# REQ-NF-010  Command-line interface
# ---------------------------------------------------------------------------

class TestCLI:
    """REQ-NF-010: The application shall provide a simple command-line
    interface with clear menu options and status feedback for user actions."""

    def test_menu_shows_create_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "1" in output
        assert "create" in output.lower() or "new" in output.lower()

    def test_menu_shows_list_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "2" in output
        assert "list" in output.lower() or "todo" in output.lower()

    def test_menu_shows_complete_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "3" in output

    def test_menu_shows_edit_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "4" in output
        assert "edit" in output.lower() or "update" in output.lower()

    def test_menu_shows_delete_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "5" in output
        assert "delete" in output.lower() or "remove" in output.lower()

    def test_menu_shows_exit_option(self, app, capsys):
        app.show_menu()
        output = capsys.readouterr().out
        assert "6" in output
        assert "exit" in output.lower() or "quit" in output.lower()

    def test_run_exits_on_choice_6(self, app, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda _: "6")
        app.run()
        output = capsys.readouterr().out
        assert "goodbye" in output.lower() or "bye" in output.lower() or "👋" in output

    def test_run_handles_invalid_choice(self, app, monkeypatch, capsys):
        """Invalid menu choice shows error then exits on next iteration."""
        inputs = iter(["9", "6"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        app.run()
        output = capsys.readouterr().out
        assert "invalid" in output.lower() or "Error" in output
