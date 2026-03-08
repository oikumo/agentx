"""RED → GREEN → REFACTOR tests for TuiOutputWriter.

TuiOutputWriter is a thread-safe bridge that collects styled message calls
and writes them into a Textual RichLog widget via a registered callback.
These tests exercise the writer in isolation without starting a Textual app.
"""

import unittest
from unittest.mock import MagicMock, call

from agent_x.applications.repl_app.tui.output_writer import TuiOutputWriter


class TuiOutputWriterTest(unittest.TestCase):
    def setUp(self):
        self.writer = TuiOutputWriter()

    # ── Registration ──────────────────────────────────────────────────────────

    def test_set_callback_stores_callable(self):
        # The writer must accept a callable that it will invoke to write
        # output to the Textual pane.
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.assertIs(self.writer._callback, cb)

    def test_initial_callback_is_none(self):
        # Before set_callback() is called the writer must be safe to use
        # (calls are buffered or silently dropped, never crash).
        self.assertIsNone(self.writer._callback)

    # ── info / warning / error ────────────────────────────────────────────────

    def test_info_invokes_callback_with_markup(self):
        # info() must call the registered callback with a Rich markup string
        # that contains the message text.
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.info("hello world")
        cb.assert_called_once()
        markup = cb.call_args.args[0]
        self.assertIn("hello world", markup)

    def test_warning_invokes_callback_with_markup(self):
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.warning("something fishy")
        cb.assert_called_once()
        markup = cb.call_args.args[0]
        self.assertIn("something fishy", markup)

    def test_error_invokes_callback_with_markup(self):
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.error("boom")
        cb.assert_called_once()
        markup = cb.call_args.args[0]
        self.assertIn("boom", markup)

    def test_info_markup_contains_info_style_indicator(self):
        # The info() markup must contain a visual indicator (color or icon)
        # distinguishing it from warning/error output.
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.info("msg")
        markup = cb.call_args.args[0]
        # Must contain a Rich color tag or the info prefix character
        self.assertTrue(
            "[" in markup or "ℹ" in markup or "INFO" in markup,
            f"Expected styled markup, got: {markup!r}",
        )

    def test_warning_markup_contains_warning_style_indicator(self):
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.warning("msg")
        markup = cb.call_args.args[0]
        self.assertTrue(
            "yellow" in markup or "⚠" in markup or "WARN" in markup,
            f"Expected warning style, got: {markup!r}",
        )

    def test_error_markup_contains_error_style_indicator(self):
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.error("msg")
        markup = cb.call_args.args[0]
        self.assertTrue(
            "red" in markup or "✗" in markup or "ERROR" in markup or "❌" in markup,
            f"Expected error style, got: {markup!r}",
        )

    # ── No-callback safety ────────────────────────────────────────────────────

    def test_info_without_callback_does_not_raise(self):
        # If no callback is registered the writer must silently no-op.
        try:
            self.writer.info("safe call")
        except Exception as exc:
            self.fail(f"info() raised without callback: {exc}")

    def test_warning_without_callback_does_not_raise(self):
        try:
            self.writer.warning("safe call")
        except Exception as exc:
            self.fail(f"warning() raised without callback: {exc}")

    def test_error_without_callback_does_not_raise(self):
        try:
            self.writer.error("safe call")
        except Exception as exc:
            self.fail(f"error() raised without callback: {exc}")

    # ── unknown_command convenience ───────────────────────────────────────────

    def test_unknown_command_invokes_error_callback(self):
        # unknown_command() is a higher-level helper that formats an error
        # message for unrecognised input; it must invoke the callback.
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.unknown_command("foobar")
        cb.assert_called_once()
        markup = cb.call_args.args[0]
        self.assertIn("foobar", markup)

    def test_unknown_command_without_callback_does_not_raise(self):
        try:
            self.writer.unknown_command("ghost")
        except Exception as exc:
            self.fail(f"unknown_command() raised without callback: {exc}")

    # ── stream_token ──────────────────────────────────────────────────────────

    def test_stream_token_invokes_callback(self):
        # stream_token() forwards a raw token string to the callback; used
        # for streaming LLM output token-by-token.
        cb = MagicMock()
        self.writer.set_callback(cb)
        self.writer.stream_token("tok")
        cb.assert_called_once()

    def test_stream_token_without_callback_does_not_raise(self):
        try:
            self.writer.stream_token("tok")
        except Exception as exc:
            self.fail(f"stream_token() raised without callback: {exc}")
