import unittest
from typing import Final
from agent_x.user_sessions.session import Session

SESSION_TEST_NAME: Final[str] = "test_session_name"

class SessionTest(unittest.TestCase):
    session: Session = None

    def setUp(self):
        self.session = Session(SESSION_TEST_NAME)

    def test_session_object_properties(self):
        self.assertEqual(self.session.name, SESSION_TEST_NAME)

        with self.assertRaises(AttributeError):
            self.session.name = "other name"

        with self.assertRaises(AttributeError):
            self.session.directory = "other directory"


    def test_session_creation(self):
        self.assertEqual(self.session.name, SESSION_TEST_NAME)
        self.assertFalse(self.session.is_created())

        self.assertTrue(self.session.create())
        self.assertTrue(self.session.is_created())

        self.assertTrue(self.session.destroy())





