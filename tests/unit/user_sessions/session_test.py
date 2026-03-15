import datetime
import unittest
from pathlib import Path
from typing import Final

from streamlit import session_state

from agent_x.user_sessions.session import Session, SESSION_DEFAULT_BASE_DIRECTORY, SESSION_DEFAULT_NAME


class SessionTest(unittest.TestCase):
    session: Session = None

    def setUp(self):
        session = None

    def test_session_object_creation_default_base_directory(self):
        session_name: Final[str] = "test_session"
        self.session = Session(session_name)
        self.assertEqual(self.session.name, session_name)
        self.assertEqual(self.session.directory, None)

    def test_session_object_creation_default_name(self):
        self.session = Session("")
        self.assertEqual(self.session.name, SESSION_DEFAULT_NAME)
        self.assertEqual(self.session.directory, None)

        self.session = Session("  ")
        self.assertEqual(self.session.name, SESSION_DEFAULT_NAME)
        self.assertEqual(self.session.directory, None)

        self.session = Session("x x")
        self.assertEqual(self.session.name, "x_x")
        self.assertEqual(self.session.directory, None)

        self.session = Session(None)
        self.assertEqual(self.session.name, SESSION_DEFAULT_NAME)
        self.assertEqual(self.session.directory, None)

    def test_session_creation(self):
        session_name: Final[str] = "test_session"
        self.session = Session(session_name)
        self.assertEqual(self.session.name, session_name)
        self.assertEqual(self.session.directory, None)
        self.assertTrue(self.session.create())
        self.assertTrue(self.session.is_created())



