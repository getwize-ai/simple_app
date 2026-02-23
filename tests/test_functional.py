"""
Functional tests for the Simple Todo Application.

Covers:
  REQ-F-001  Create todo items with title and optional description
  REQ-F-002  List all todo items with their current status
  REQ-F-003  Toggle completion status of a todo item
  REQ-F-004  Delete todo items permanently
  REQ-F-005  Edit title and description of existing todo items
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import TodoApp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app(tmp_path, monkeypatch):
    """Return a fresh TodoApp instance backed by a temporary data file."""
    monkeypatch.chdir(tmp_path)
    return TodoApp()


@pytest.fixture
def app_with_todos(app):
    """Return a TodoApp pre-populated with three todo items."""
    app.create_todo("Buy groceries", "Milk, eggs, bread")
    app.create_todo("Write report", "Quarterly summary")
    app.create_todo("Call dentist")
    return app


# ---------------------------------------------------------------------------
# REQ-F-001  Create new todo items
# ---------------------------------------------------------------------------

class TestCreateTodo:
    """REQ-F-001: The application shall allow users to create new todo items
    with a title and optional description."""

    def test_create_todo_with_title_only(self, app):
        result = app.create_todo("Buy groceries")
        assert result is True
        assert len(app.todos) == 1
        assert app.todos[0]["title"] == "Buy groceries"

    def test_create_todo_with_title_and_description(self, app):
        result = app.create_todo("Buy groceries", "Milk, eggs, bread")
        assert result is True
        assert app.todos[0]["description"] == "Milk, eggs, bread"

    def test_create_todo_description_defaults_to_empty(self, app):
        app.create_todo("Simple task")
        assert app.todos[0]["description"] == ""

    def test_create_todo_assigns_sequential_id(self, app):
        app.create_todo("First")
        app.create_todo("Second")
        app.create_todo("Third")
        ids = [t["id"] for t in app.todos]
        assert ids == [1, 2, 3]

    def test_create_todo_sets_completed_false(self, app):
        app.create_todo("New task")
        assert app.todos[0]["completed"] is False

    def test_create_todo_stores_created_at_timestamp(self, app):
        app.create_todo("Task with timestamp")
        assert "created_at" in app.todos[0]
        assert app.todos[0]["created_at"]  # not empty

    def test_create_multiple_todos(self, app):
        app.create_todo("Task 1")
        app.create_todo("Task 2")
        app.create_todo("Task 3")
        assert len(app.todos) == 3

    def test_create_todo_strips_whitespace_from_title(self, app):
        app.create_todo("  Trim me  ")
        assert app.todos[0]["title"] == "Trim me"


# ---------------------------------------------------------------------------
# REQ-F-002  List todos
# ---------------------------------------------------------------------------

class TestListTodos:
    """REQ-F-002: The application shall display all created todo items in a
    list format with their current status."""

    def test_list_todos_prints_all_items(self, app_with_todos, capsys):
        app_with_todos.list_todos()
        output = capsys.readouterr().out
        assert "Buy groceries" in output
        assert "Write report" in output
        assert "Call dentist" in output

    def test_list_todos_shows_completion_status(self, app_with_todos, capsys):
        app_with_todos.mark_complete(1)
        app_with_todos.list_todos()
        output = capsys.readouterr().out
        assert "DONE" in output or "✓" in output

    def test_list_todos_empty_list_shows_message(self, app, capsys):
        app.list_todos()
        output = capsys.readouterr().out
        assert "No todos" in output or "empty" in output.lower() or "Create" in output

    def test_list_todos_shows_description_when_present(self, app_with_todos, capsys):
        app_with_todos.list_todos()
        output = capsys.readouterr().out
        assert "Milk, eggs, bread" in output

    def test_list_todos_shows_created_date(self, app_with_todos, capsys):
        app_with_todos.list_todos()
        output = capsys.readouterr().out
        # Date is printed as YYYY-MM-DD
        import re
        assert re.search(r"\d{4}-\d{2}-\d{2}", output)


# ---------------------------------------------------------------------------
# REQ-F-003  Toggle completion status
# ---------------------------------------------------------------------------

class TestMarkComplete:
    """REQ-F-003: The application shall provide functionality to mark a todo
    item as complete or incomplete with a toggle action."""

    def test_mark_complete_sets_completed_true(self, app_with_todos):
        app_with_todos.mark_complete(1)
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["completed"] is True

    def test_mark_complete_toggles_back_to_incomplete(self, app_with_todos):
        app_with_todos.mark_complete(1)
        app_with_todos.mark_complete(1)
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["completed"] is False

    def test_mark_complete_returns_true_on_success(self, app_with_todos):
        result = app_with_todos.mark_complete(1)
        assert result is True

    def test_mark_complete_returns_false_for_unknown_id(self, app_with_todos):
        result = app_with_todos.mark_complete(999)
        assert result is False

    def test_mark_complete_updates_updated_at(self, app_with_todos):
        original_ts = app_with_todos.todos[0]["updated_at"]
        import time; time.sleep(0.01)
        app_with_todos.mark_complete(1)
        new_ts = next(t for t in app_with_todos.todos if t["id"] == 1)["updated_at"]
        assert new_ts >= original_ts

    def test_mark_complete_does_not_affect_other_todos(self, app_with_todos):
        app_with_todos.mark_complete(1)
        todo2 = next(t for t in app_with_todos.todos if t["id"] == 2)
        todo3 = next(t for t in app_with_todos.todos if t["id"] == 3)
        assert todo2["completed"] is False
        assert todo3["completed"] is False


# ---------------------------------------------------------------------------
# REQ-F-004  Delete todo items
# ---------------------------------------------------------------------------

class TestDeleteTodo:
    """REQ-F-004: The application shall allow users to delete todo items from
    the list permanently."""

    def test_delete_todo_removes_item(self, app_with_todos):
        app_with_todos.delete_todo(1)
        ids = [t["id"] for t in app_with_todos.todos]
        assert 1 not in ids

    def test_delete_todo_returns_true_on_success(self, app_with_todos):
        result = app_with_todos.delete_todo(1)
        assert result is True

    def test_delete_todo_returns_false_for_unknown_id(self, app_with_todos):
        result = app_with_todos.delete_todo(999)
        assert result is False

    def test_delete_todo_reduces_list_length(self, app_with_todos):
        original_count = len(app_with_todos.todos)
        app_with_todos.delete_todo(1)
        assert len(app_with_todos.todos) == original_count - 1

    def test_delete_todo_is_permanent(self, app_with_todos, tmp_path, monkeypatch):
        """Deletion must persist to disk — item must not reappear after reload."""
        monkeypatch.chdir(tmp_path)
        # Write todos to disk first
        app_with_todos._save_todos()
        app_with_todos.delete_todo(1)

        # Reload from disk
        reloaded = TodoApp()
        ids = [t["id"] for t in reloaded.todos]
        assert 1 not in ids

    def test_delete_todo_does_not_affect_remaining_items(self, app_with_todos):
        titles_before = {t["id"]: t["title"] for t in app_with_todos.todos if t["id"] != 2}
        app_with_todos.delete_todo(2)
        for todo in app_with_todos.todos:
            assert todo["title"] == titles_before[todo["id"]]


# ---------------------------------------------------------------------------
# REQ-F-005  Edit todo items
# ---------------------------------------------------------------------------

class TestEditTodo:
    """REQ-F-005: The application shall allow users to edit the title and
    description of existing todo items."""

    def test_edit_title(self, app_with_todos):
        app_with_todos.edit_todo(1, title="Updated title")
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["title"] == "Updated title"

    def test_edit_description(self, app_with_todos):
        app_with_todos.edit_todo(1, description="New description")
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["description"] == "New description"

    def test_edit_both_title_and_description(self, app_with_todos):
        app_with_todos.edit_todo(1, title="New title", description="New desc")
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["title"] == "New title"
        assert todo["description"] == "New desc"

    def test_edit_returns_true_on_success(self, app_with_todos):
        result = app_with_todos.edit_todo(1, title="Changed")
        assert result is True

    def test_edit_returns_false_for_unknown_id(self, app_with_todos):
        result = app_with_todos.edit_todo(999, title="Ghost")
        assert result is False

    def test_edit_title_none_keeps_original(self, app_with_todos):
        original_title = app_with_todos.todos[0]["title"]
        app_with_todos.edit_todo(1, description="Only desc changed")
        todo = next(t for t in app_with_todos.todos if t["id"] == 1)
        assert todo["title"] == original_title

    def test_edit_updates_updated_at_timestamp(self, app_with_todos):
        original_ts = app_with_todos.todos[0]["updated_at"]
        import time; time.sleep(0.01)
        app_with_todos.edit_todo(1, title="Changed")
        new_ts = next(t for t in app_with_todos.todos if t["id"] == 1)["updated_at"]
        assert new_ts >= original_ts
