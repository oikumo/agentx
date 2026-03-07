import unittest
import os
import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path

from agent_x.user_sessions.session import Session


class SessionTest(unittest.TestCase):
    def test_session_creation_with_valid_name(self):
        session = Session("test_session")
        self.assertEqual(session.name, "test_session")
        self.assertEqual(session.directory, "")

    def test_session_creation_with_empty_name_raises_exception(self):
        with self.assertRaises(Exception):
            Session("")

    def test_session_creation_with_whitespace_name(self):
        with self.assertRaises(Exception):
            Session("   ")

    def test_session_name_assignment(self):
        session = Session("my_session")
        self.assertEqual(session.name, "my_session")

    # ── Session.create() ──────────────────────────────────────────────────────

    def test_create_makes_directory_and_sets_directory_attribute(self):
        # create() must build the sessions/web_ingestion/<name>/<datetime>/
        # path and populate self.directory with its absolute Path.
        session = Session("test_project")

        # Pin the datetime so the expected path is deterministic.
        fixed_dt = datetime.datetime(2026, 3, 7, 12, 0, 0)

        with (
            patch("agent_x.user_sessions.session.datetime") as mock_dt,
            patch("agent_x.user_sessions.session.os.path.isdir") as mock_isdir,
            patch.object(Path, "mkdir") as mock_mkdir,
        ):
            # datetime.datetime.now() returns our fixed datetime.
            mock_dt.datetime.now.return_value = fixed_dt

            # First call: directory does not exist yet (pre-creation check).
            # Second call: directory exists after mkdir (post-creation check).
            mock_isdir.side_effect = [False, True]

            session.create()

            # mkdir must have been called exactly once (parents=True, exist_ok=True).
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

            # self.directory must be set (non-empty) after a successful create().
            self.assertIsNotNone(session.directory)
            self.assertNotEqual(session.directory, "")

    def test_create_raises_file_exists_error_when_directory_already_exists(self):
        # If the target directory already exists, create() must raise
        # FileExistsError rather than silently overwriting prior session data.
        session = Session("my_project")

        fixed_dt = datetime.datetime(2026, 3, 7, 12, 0, 0)

        with (
            patch("agent_x.user_sessions.session.datetime") as mock_dt,
            patch("agent_x.user_sessions.session.os.path.isdir", return_value=True),
        ):
            mock_dt.datetime.now.return_value = fixed_dt

            with self.assertRaises(FileExistsError):
                session.create()

    def test_create_uses_session_name_in_directory_path(self):
        # The session name must appear in the constructed path so different
        # projects don't share the same directory.
        session = Session("unique_project_name")

        fixed_dt = datetime.datetime(2026, 3, 7, 12, 0, 0)

        with (
            patch("agent_x.user_sessions.session.datetime") as mock_dt,
            patch("agent_x.user_sessions.session.os.path.isdir") as mock_isdir,
            patch.object(Path, "mkdir"),
        ):
            mock_dt.datetime.now.return_value = fixed_dt
            mock_isdir.side_effect = [False, True]

            session.create()

            # The absolute path string must contain the session name.
            self.assertIn("unique_project_name", str(session.directory))
