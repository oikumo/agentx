"""
Unit tests for agentx.model.db.session_db module.

Tests cover:
- HistoryEntry: Data structure for history entries
- TableHistory: Table schema and operations
- TableUser: User table schema
- History: Data structure for history records
"""

import pytest
from dataclasses import fields

from agentx.model.db.session_db import (
    HistoryEntry,
    TableHistory,
    TableUser,
)


# History is defined as a nested class in TableHistory in the source
# We need to access it from there
try:
    # Try to get History from the module level (it might be exported)
    from agentx.model.db.session_db import History
except ImportError:
    # Or access it from TableHistory class
    History = TableHistory.History


class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""

    def test_create_history_entry(self):
        """Test creating HistoryEntry instance."""
        entry = HistoryEntry(command="test command")
        assert entry.command == "test command"
        assert entry.id == 0
        assert entry.created_at == ""

    def test_create_history_entry_with_all_fields(self):
        """Test creating HistoryEntry with all fields."""
        entry = HistoryEntry(
            command="test",
            id=1,
            created_at="2024-01-01 00:00:00"
        )
        assert entry.command == "test"
        assert entry.id == 1
        assert entry.created_at == "2024-01-01 00:00:00"

    def test_history_entry_fields(self):
        """Test that HistoryEntry has correct fields."""
        entry = HistoryEntry(command="test")
        field_names = [f.name for f in fields(entry)]
        assert "command" in field_names
        assert "id" in field_names
        assert "created_at" in field_names


class TestTableHistory:
    """Tests for TableHistory class."""

    def test_table_name(self):
        """Test table name constant."""
        assert TableHistory.TABLE_NAME == "history"

    def test_table_history_schema(self):
        """Test table creation schema."""
        assert "CREATE TABLE" in TableHistory.TABLE_HISTORY
        assert "history" in TableHistory.TABLE_HISTORY
        assert "id INTEGER PRIMARY KEY" in TableHistory.TABLE_HISTORY
        assert "command TEXT" in TableHistory.TABLE_HISTORY
        assert "created_at TIMESTAMP" in TableHistory.TABLE_HISTORY

    def test_insert_history_query(self):
        """Test insert query."""
        assert "INSERT INTO" in TableHistory.INSERT_HISTORY
        assert "history" in TableHistory.INSERT_HISTORY
        assert "command" in TableHistory.INSERT_HISTORY
        assert "created_at" in TableHistory.INSERT_HISTORY
        assert "?" in TableHistory.INSERT_HISTORY  # Parameterized query


class TestTableUser:
    """Tests for TableUser class."""

    def test_table_name(self):
        """Test users table name."""
        assert TableUser.TABLE_NAME == "users"

    def test_table_user_schema(self):
        """Test user table creation schema."""
        assert "CREATE TABLE" in TableUser.TABLE_USER
        assert "users" in TableUser.TABLE_USER
        assert "id INTEGER PRIMARY KEY" in TableUser.TABLE_USER
        assert "name TEXT" in TableUser.TABLE_USER
        assert "age INTEGER" in TableUser.TABLE_USER

    def test_insert_user_query(self):
        """Test user insert query."""
        assert "INSERT INTO" in TableUser.INSERT_USER
        assert "users" in TableUser.INSERT_USER
        assert "name" in TableUser.INSERT_USER
        assert "age" in TableUser.INSERT_USER
        assert "?" in TableUser.INSERT_USER  # Parameterized query


class TestHistory:
    """Tests for History dataclass."""

    def test_create_history(self):
        """Test creating History instance."""
        history = History(id=1, command="test", created_at="2024-01-01")
        assert history.id == 1
        assert history.command == "test"
        assert history.created_at == "2024-01-01"

    def test_history_fields(self):
        """Test that History has correct fields."""
        history = History(id=1, command="test", created_at="now")
        field_names = [f.name for f in fields(history)]
        assert "id" in field_names
        assert "command" in field_names
        assert "created_at" in field_names

    def test_history_default_values(self):
        """Test History requires all fields (no defaults)."""
        # All fields are required
        history = History(id=0, command="", created_at="")
        assert history.id == 0
        assert history.command == ""
        assert history.created_at == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
