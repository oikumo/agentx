"""Root conftest.py — pytest session-level configuration.

Problem: Textual's IsolatedAsyncioTestCase installs a custom asyncio event
loop policy that persists after the test class finishes.  Tests that call
asyncio.get_event_loop().run_until_complete() (the web_ingestion_app test
suite) then fail with "There is no current event loop in thread 'MainThread'".

Fix: after every test item that belongs to an IsolatedAsyncioTestCase, reset
the asyncio policy to the platform default so the next test starts clean.
"""

import asyncio
import unittest


def pytest_runtest_teardown(item, nextitem):
    """Reset asyncio policy after any IsolatedAsyncioTestCase test."""
    test = getattr(item, "obj", None)
    if test is None:
        return
    cls = getattr(test, "__self__", None)
    if cls is None:
        return
    if isinstance(cls, unittest.IsolatedAsyncioTestCase):
        asyncio.set_event_loop_policy(None)
        # Create a fresh event loop for synchronous tests that follow.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
