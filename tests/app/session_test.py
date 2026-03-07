import unittest

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
