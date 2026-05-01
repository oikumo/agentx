"""
Unit tests for agentx.model.session.session module.

Tests cover:
- Session: Creation, naming, directory management
- SessionDatabase: Database operations, history tracking
"""

import os
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
import pytest

from agentx.model.session.session import Session, SessionDatabase
from agentx.common.security import SESSION_DEFAULT_NAME, SESSION_DEFAULT_BASE_DIRECTORY


class TestSession:
    """Tests for Session class."""

    def test_create_session_default_name(self):
        """Test creating session with default name."""
        session = Session("")
        assert session.name == SESSION_DEFAULT_NAME

    def test_create_session_with_name(self):
        """Test creating session with custom name."""
        session = Session("test_session")
        assert session.name == "test_session"

    def test_create_session_with_spaces(self):
        """Test that spaces in name are replaced with underscores."""
        session = Session("test session name")
        assert session.name == "test_session_name"

    def test_create_session_empty_name(self):
        """Test creating session with empty name uses default."""
        session = Session("   ")
        assert session.name == SESSION_DEFAULT_NAME

    def test_session_initial_directory(self):
        """Test session initial directory is None."""
        session = Session("test")
        assert session.directory is None

    def test_session_not_created_initially(self):
        """Test session is not created initially."""
        session = Session("test")
        assert session.is_created() is False

    @patch("agentx.model.session.session.create_directory_with_timestamp")
    @patch("agentx.model.session.session.directory_exists")
    def test_session_create_success(self, mock_exists, mock_create_dir):
        """Test successful session creation."""
        mock_create_dir.return_value = "/fake/path/test_2024-01-01"
        mock_exists.return_value = True

        session = Session("test", use_timestamp=True)
        result = session.create()

        assert result is True
        assert session.directory == "/fake/path/test_2024-01-01"
        assert session.is_created() is True
        mock_create_dir.assert_called_once()

    @patch("agentx.model.session.session.create_directory_without_timestamp")
    @patch("agentx.model.session.session.directory_exists")
    def test_session_create_without_timestamp(self, mock_exists, mock_create_dir):
        """Test session creation without timestamp."""
        mock_create_dir.return_value = "/fake/path/test"
        mock_exists.return_value = True

        session = Session("test", use_timestamp=False)
        result = session.create()

        assert result is True
        mock_create_dir.assert_called_once_with("test", SESSION_DEFAULT_BASE_DIRECTORY)

    @patch("agentx.model.session.session.create_directory_with_timestamp")
    def test_session_create_failure(self, mock_create_dir):
        """Test session creation failure."""
        mock_create_dir.return_value = None

        session = Session("test")
        result = session.create()

        assert result is False
        assert session.directory is None


class TestSessionDatabase:
    """Tests for SessionDatabase class."""

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_create_database(self, mock_connect):
        """Test database creation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)

        # Verify tables were created
        assert mock_cursor.execute.call_count >= 2

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_get_session_path(self, mock_connect):
        """Test getting session database path."""
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)
        path = db._get_session_path()

        assert "test.db" in str(path)

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_insert_history_entry(self, mock_connect):
        """Test inserting history entry."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)
        result = db.insert_history_entry("test command")

        assert result is True
        mock_cursor.execute.assert_called()

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_select_history_entry(self, mock_connect):
        """Test selecting history entries."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall to return test data
        mock_cursor.fetchall.return_value = [
            (1, "command1", "2024-01-01 00:00:00"),
            (2, "command2", "2024-01-01 00:01:00"),
        ]

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)
        entries = db.select_history_entry()

        assert entries is not None
        assert len(entries) == 2

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_select_empty_history(self, mock_connect):
        """Test selecting from empty history."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)
        entries = db.select_history_entry()

        assert entries is None

    @patch("agentx.model.session.session.sqlite3.connect")
    def test_invalid_table_select(self, mock_connect):
        """Test that selecting from invalid table raises error."""
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn

        session = MagicMock()
        session.directory = "/fake/path"
        session.name = "test"

        db = SessionDatabase(session)

        with pytest.raises(ValueError, match="Invalid table name"):
            db._select_all("invalid_table")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
