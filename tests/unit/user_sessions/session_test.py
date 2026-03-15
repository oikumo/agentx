import unittest
from typing import Final
from agent_x.user_sessions.session import Session

SESSION_TEST_NAME: Final[str] = "test_session_name"

class SessionTest(unittest.TestCase):
    def test_session_object_properties(self):
        session = Session(SESSION_TEST_NAME)
        self.assertEqual(session.name, SESSION_TEST_NAME)

        with self.assertRaises(AttributeError):
            session.name = "other name"

        with self.assertRaises(AttributeError):
            session.directory = "other directory"


    def test_session_creation(self):
        session = Session(SESSION_TEST_NAME)
        self.assertEqual(session.name, SESSION_TEST_NAME)
        self.assertFalse(session.is_created())

        self.assertTrue(session.create())
        self.assertTrue(session.is_created())

        self.assertTrue(session.destroy())

        self.assertFalse(session.is_created())





