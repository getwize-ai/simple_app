#!/usr/bin/env python3
"""
Simple Todo Application

This application implements a command-line todo list manager that persists
data to JSON and provides full CRUD operations with validation.

"""

import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class TodoApp:
    
    DATA_FILE = "todos.json"
    MAX_TITLE_LENGTH = 200
    
    def __init__(self):
        """Initialize the application with data persistence."""
        self.todos: List[Dict[str, Any]] = []
        self._load_todos()
    
    def _load_todos(self) -> None:

        try:
            if Path(self.DATA_FILE).exists():
                with open(self.DATA_FILE, 'r') as f:
                    self.todos = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Could not load todos: {e}. Starting with empty list.")
            self.todos = []
    
    def _save_todos(self) -> None:

        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(self.todos, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save todos: {e}") 
    
    def _validate_title(self, title: str) -> bool:
        """
        Validate todo title.
        
        Args:
            title: The title to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not title or not title.strip():
            print("❌ Error: Title cannot be empty")
            return False
        
        if len(title) > self.MAX_TITLE_LENGTH:
            print(f"❌ Error: Title cannot exceed {self.MAX_TITLE_LENGTH} characters")
            return False
        
        return True
    
    def create_todo(self, title: str, description: str = "") -> bool:
        """
        Create a new todo item.

        Args:
            title: The todo title
            description: Optional todo description
            
        Returns:
            bool: True if created successfully
        """
        if not self._validate_title(title):
            return False
        
        try:
            todo = {
                "id": len(self.todos) + 1,
                "title": title.strip(),
                "description": description.strip(),
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.todos.append(todo)
            self._save_todos()
            print(f"✅ Todo created: '{title}'")
            return True
        except Exception as e:
            print(f"❌ Error creating todo: {e}")
            return False
    
    def list_todos(self) -> None:
        """
        Display all todos in a formatted list.
        """
        if not self.todos:
            print("\n📋 No todos yet. Create one to get started!")
            return
        
        print("\n📋 Your Todos:")
        print("=" * 70)
        
        for todo in self.todos:
            status = "✓" if todo["completed"] else "○"
            completed_text = "[DONE]" if todo["completed"] else "[TODO]"
            
            print(f"\n  {status} [{todo['id']}] {completed_text} {todo['title']}")
            
            if todo["description"]:
                print(f"      Description: {todo['description']}")
            
            print(f"      Created: {todo['created_at'][:10]}")
        
        print("\n" + "=" * 70)
    
    def mark_complete(self, todo_id: int) -> bool:
        """
        Mark a todo as complete or toggle completion status.
        
        Args:
            todo_id: The ID of the todo to mark complete
            
        Returns:
            bool: True if successful
        """
        try:
            for todo in self.todos:
                if todo["id"] == todo_id:
                    todo["completed"] = not todo["completed"]
                    todo["updated_at"] = datetime.now().isoformat()
                    self._save_todos()
                    
                    status = "completed" if todo["completed"] else "reopened"
                    print(f"✅ Todo {status}: '{todo['title']}'")
                    return True
            
            print(f"❌ Error: Todo with ID {todo_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error marking todo: {e}") 
            return False
    
    def delete_todo(self, todo_id: int) -> bool:
        """
        Delete a todo item.

        Args:
            todo_id: The ID of the todo to delete
            
        Returns:
            bool: True if successful
        """
        try:
            original_length = len(self.todos)
            self.todos = [t for t in self.todos if t["id"] != todo_id]
            
            if len(self.todos) < original_length:
                self._save_todos()
                print(f"✅ Todo deleted")
                return True
            else:
                print(f"❌ Error: Todo with ID {todo_id} not found")
                return False
        except Exception as e:
            print(f"❌ Error deleting todo: {e}") 
            return False
    
    def edit_todo(self, todo_id: int, title: Optional[str] = None, 
                  description: Optional[str] = None) -> bool:
        """
        Edit an existing todo item.
        
        Args:
            todo_id: The ID of the todo to edit
            title: New title (optional)
            description: New description (optional)
            
        Returns:
            bool: True if successful
        """
        try:
            for todo in self.todos:
                if todo["id"] == todo_id:
                    if title is not None:
                        if not self._validate_title(title):
                            return False
                        todo["title"] = title.strip()
                    
                    if description is not None:
                        todo["description"] = description.strip()
                    
                    todo["updated_at"] = datetime.now().isoformat()
                    self._save_todos()
                    print(f"✅ Todo updated: '{todo['title']}'")
                    return True
            
            print(f"❌ Error: Todo with ID {todo_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error editing todo: {e}")
            return False
    
    def show_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 70)
        print("📝 Todo Application")
        print("=" * 70)
        print("1. Create new todo")
        print("2. List all todos")
        print("3. Mark todo complete/incomplete")
        print("4. Edit todo")
        print("5. Delete todo")
        print("6. Exit")
        print("=" * 70)
    
    def run(self) -> None:
        """Main application loop."""
        print("\n🚀 Welcome to the Simple Todo Application!")
        
        while True:
            self.show_menu()
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                title = input("Enter todo title: ").strip()
                description = input("Enter description (optional): ").strip()
                self.create_todo(title, description)
            
            elif choice == "2":
                self.list_todos()
            
            elif choice == "3":
                self.list_todos()
                try:
                    todo_id = int(input("Enter todo ID to toggle: "))
                    self.mark_complete(todo_id)
                except ValueError:
                    print("❌ Error: Please enter a valid ID number")
            
            elif choice == "4":
                self.list_todos()
                try:
                    todo_id = int(input("Enter todo ID to edit: "))
                    title = input("Enter new title (leave empty to skip): ").strip()
                    description = input("Enter new description (leave empty to skip): ").strip()
                    
                    new_title = title if title else None
                    new_description = description if description else None
                    
                    self.edit_todo(todo_id, new_title, new_description)
                except ValueError:
                    print("❌ Error: Please enter a valid ID number")
            
            elif choice == "5":
                self.list_todos()
                try:
                    todo_id = int(input("Enter todo ID to delete: "))
                    confirm = input(f"Are you sure? (yes/no): ").strip().lower()
                    if confirm == "yes":
                        self.delete_todo(todo_id)
                except ValueError:
                    print("❌ Error: Please enter a valid ID number")
            
            elif choice == "6":
                print("\n👋 Goodbye! Your todos have been saved.")
                break
            
            else:
                print("❌ Error: Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    app = TodoApp()
    app.run()
