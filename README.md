# Simple Todo Application

A command-line todo list manager with persistent JSON storage.

## Overview

This is a simple yet complete todo application that demonstrates:
- Functional requirements implementation (CRUD operations)
- Non-functional requirements (persistence, validation, performance, error handling)
- Clean code architecture with proper error handling
- Data persistence using JSON

## Requirements Implemented

### Functional Requirements

- **REQ-001**: Create Todo Items - Add new todos with title and optional description
- **REQ-002**: List Todo Items - Display all todos with status and metadata
- **REQ-003**: Mark Todo as Complete - Toggle completion status on/off
- **REQ-004**: Delete Todo Items - Remove todos from the list permanently
- **REQ-005**: Edit Todo Items - Update title and description of existing todos

### Non-Functional Requirements

- **REQ-006**: Data Persistence - All todos saved to `todos.json` file
- **REQ-007**: Input Validation - Titles validated (non-empty, max 200 chars)
- **REQ-008**: Performance - All operations complete within 100ms
- **REQ-009**: Code Quality - Comprehensive error handling with descriptive messages
- **REQ-010**: User Interface - Simple CLI with menu-driven interface

## Features

✅ Create, Read, Update, Delete (CRUD) todos
✅ Toggle completion status
✅ Persistent storage (JSON)
✅ Input validation
✅ Error handling
✅ Clear CLI interface
✅ Timestamps for created/updated dates

## Usage

```bash
python app.py
```

### Menu Options

```
1. Create new todo          - Add a new todo item
2. List all todos          - View all todos with status
3. Mark todo complete      - Toggle todo completion status
4. Edit todo               - Update title or description
5. Delete todo             - Remove a todo permanently
6. Exit                    - Save and quit application
```

## Data Storage

All todos are persisted in `todos.json` with the following structure:

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-09T10:30:00",
    "updated_at": "2025-12-09T10:30:00"
  }
]
```

## File Structure

```
simple_app/
├── requirements.md    - 10 requirements for the application
├── app.py            - Main application implementation
└── README.md         - This file
```

## Requirements Traceability

Each requirement is implemented and can be traced in the code:

| REQ ID | Feature | Implementation | Status |
|--------|---------|-----------------|--------|
| REQ-001 | Create todos | `create_todo()` method | ✅ |
| REQ-002 | List todos | `list_todos()` method | ✅ |
| REQ-003 | Mark complete | `mark_complete()` method | ✅ |
| REQ-004 | Delete todos | `delete_todo()` method | ✅ |
| REQ-005 | Edit todos | `edit_todo()` method | ✅ |
| REQ-006 | Data persistence | `_load_todos()`, `_save_todos()` | ✅ |
| REQ-007 | Input validation | `_validate_title()` method | ✅ |
| REQ-008 | Performance | JSON operations, efficient filtering | ✅ |
| REQ-009 | Error handling | Try-except blocks, error messages | ✅ |
| REQ-010 | CLI interface | `show_menu()`, `run()` methods | ✅ |

## Example Session

```
🚀 Welcome to the Simple Todo Application!

════════════════════════════════════════════════════════════════════
📝 Todo Application
════════════════════════════════════════════════════════════════════
1. Create new todo
2. List all todos
3. Mark todo complete/incomplete
4. Edit todo
5. Delete todo
6. Exit
════════════════════════════════════════════════════════════════════
Enter your choice (1-6): 1
Enter todo title: Buy groceries
Enter description (optional): Milk, eggs, bread
✅ Todo created: 'Buy groceries'

📋 Your Todos:
════════════════════════════════════════════════════════════════════

  ○ [1] [TODO] Buy groceries
      Description: Milk, eggs, bread
      Created: 2025-12-09

════════════════════════════════════════════════════════════════════
```

## Error Handling

The application provides clear error messages for:
- Empty titles
- Titles exceeding 200 characters
- Invalid todo IDs
- File I/O errors
- Invalid menu selections

## Performance

All operations are optimized:
- JSON file read on startup only
- Linear search for todo lookups (acceptable for typical use)
- Single file write per operation
- No external dependencies

## Code Quality

- Type hints for all function parameters
- Comprehensive docstrings
- Clear variable names
- Proper error handling throughout
- Separation of concerns (UI, data, logic)
