#!/usr/bin/env python3
"""Real-opencode e2e test for feature_020 plugin loading.

This is a TRUE end-to-end test (unlike test_omt_nav.py's function-level checks
via _nav_runner.mjs, which never actually run opencode). It spawns a real
`opencode serve` process, triggers config bootstrap (which loads the plugins),
and asserts on the stderr log stream that all three OMT++ plugins load cleanly.

This test exists specifically to catch two latent defects that the
function-level tests gave false confidence about (see WORK.md Resume Plan):

  - DEFECT A: `omt_nav.ts` exports tools as named exports only
    (`export { omt_nav, ... }`). opencode requires a default plugin FUNCTION
    (`export default async () => ({tool: {...}})`). With only named exports,
    `omt_nav/omt_list_sections/omt_cross_ref/omt_quick_ref` are NEVER registered
    in a real opencode session — the feature_020 nav-gate is a catch-22 (the
    gate blocks doc grep/glob but the nav tools that satisfy it don't exist
    in-session).

  - DEFECT B: `omt_enforcer.ts` `getSearchPath()` returns a repo-relative path
    via `relOf(raw).rel`, where `raw` is taken from
    `output?.args?.path ?? ... ?? .file`. In a real opencode tool call these
    can be arrays/objects, not strings; `isDocPath()` then calls `.startsWith`
    on a non-string and throws. The plugin crashes in serve mode at bootstrap.
    It survives in TUI mode because path-less globs make `targetRel` null.
    The fix must not regress TUI behavior.

Run with:
    uv run pytest tests/features/feature_020.meta_harness_navigation/test_opencode_e2e.py -q
"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGINS = {
    "omt_status.ts": "omt_status.ts (control: must load)",
    "omt_enforcer.ts": "omt_enforcer.ts (DEFECT B: must not crash on non-string path)",
    "omt_nav.ts": "omt_nav.ts (DEFECT A: must export default plugin fn)",
}
OPENCODE = shutil.which("opencode")
needs_opencode = pytest.mark.skipif(not OPENCODE, reason="opencode not available")


def _free_port() -> int:
    """Get a free localhost port for the serve instance."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_listen(proc: subprocess.Popen, port: int, timeout: float = 15.0) -> bool:
    """Poll a tcp socket until opencode serve prints it's listening.

    The serve stdout emits `opencode server listening on http://127.0.0.1:<port>`.
    We match that to know the server is ready before hitting /config (which is
    what triggers bootstrap → plugin loading). Returns True on success.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def _capture_serve(
    port: int, pure: bool = False, boot_timeout: float = 20.0
) -> str:
    """Spawn opencode serve, trigger bootstrap, return stderr log text.

    Plugins load lazily during bootstrap, which is triggered by an HTTP request
    that requires a project instance (e.g. /config). We run with
    --print-logs=true and --log-level=DEBUG so the plugin-load events (incl.
    failures) are emitted on stderr.

    Timing note: the TCP port accepts connections before opencode's HTTP routes
    are fully wired. _wait_for_listen returns the instant the port is bound, so
    we add a short settle delay before hitting /config — otherwise /config can
    time out and bootstrap never fires (false-green).
    """
    assert OPENCODE, "opencode binary required"
    args = [OPENCODE, "serve", "--port", str(port), "--print-logs=true", "--log-level=DEBUG"]
    if pure:
        args.append("--pure")
    env = dict(os.environ)
    proc = subprocess.Popen(
        args,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    try:
        if not _wait_for_listen(proc, port, timeout=15.0):
            proc.kill()
            out, err = proc.communicate(timeout=5)
            pytest.fail(
                f"opencode serve did not listen on port {port} within 15s.\n"
                f"stdout=\n{out}\nstderr=\n{err}"
            )
        # Settle: the port binds before HTTP routes are ready. Without this
        # delay /config times out and bootstrap (→ plugin loading) never fires.
        time.sleep(1.5)
        # Trigger bootstrap by hitting /config; this loads the project instance
        # and the plugins.
        try:
            import urllib.request

            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/config", timeout=10
            ) as resp:
                resp.read()  # drain
        except Exception:
            pass
        # Give plugin loading a moment to flush to stderr
        time.sleep(2.0)
        # Terminate gracefully so logs flush
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=5)
        return err
    finally:
        try:
            if proc.poll() is None:
                proc.kill()
                proc.communicate(timeout=3)
        except Exception:
            pass


_PLUGIN_FAIL_RE = re.compile(
    r'failed to load plugin[^"]*path=file://[^"]*?([^/"]+\.ts)[^"]*"?'
    r'(?:error="([^"]+)")?',
    re.IGNORECASE,
)


def _failed_plugins(log_text: str) -> dict[str, str]:
    """Parse stderr logs; return {plugin_filename: error_message} for each failure."""
    failures: dict[str, str] = {}
    for line in log_text.splitlines():
        if "failed to load plugin" not in line:
            continue
        # Extract the filename from the path and the error message.
        m = re.search(r'path=file://[^\s"]*?([^/"]+\.ts)', line)
        err_m = re.search(r'error="([^"]+)"', line)
        if m:
            failures[m.group(1)] = err_m.group(1) if err_m else "<unknown error>"
    return failures


@needs_opencode
class TestOpencodeServePluginLoad:
    """True e2e: real `opencode serve` actually loads the OMT++ plugins."""

    def test_all_omt_plugins_load_cleanly(self):
        """Assert no `failed to load plugin` lines for any of the three OMT++
        plugins. This catches both DEFECT A (omt_nav export-not-a-function)
        and DEFECT B (omt_enforcer .startsWith-on-non-string crash)."""
        log = _capture_serve(_free_port())
        failures = _failed_plugins(log)
        # Report which failed and why for fast diagnosis
        relevant = {k: v for k, v in failures.items() if k in PLUGINS}
        assert not relevant, (
            f"OMT++ plugins failed to load in real opencode serve:\n"
            + "\n".join(f"  - {k}: {v}" for k, v in relevant.items())
            + f"\nfull stderr tail:\n" + "\n".join(log.splitlines()[-25:])
        )

    def test_omt_status_plugin_loads(self):
        """Control: omt_status.ts uses the canonical `export default async () =>
        ({tool: {...}})` pattern and must always load. If this fails the
        environment is broken, not the plugin."""
        log = _capture_serve(_free_port())
        failures = _failed_plugins(log)
        assert "omt_status.ts" not in failures, (
            f"omt_status.ts (control) failed to load — environment issue:\n"
            f"  error: {failures.get('omt_status.ts')}\n"
            f"stderr tail:\n" + "\n".join(log.splitlines()[-25:])
        )

    def test_omt_enforcer_plugin_loads(self):
        """Specifically assert omt_enforcer.ts (DEFECT B) loads cleanly in serve
        mode, where the non-string path bug crashes it."""
        log = _capture_serve(_free_port())
        failures = _failed_plugins(log)
        assert "omt_enforcer.ts" not in failures, (
            f"omt_enforcer.ts failed to load (DEFECT B regression):\n"
            f"  error: {failures.get('omt_enforcer.ts')}\n"
            f"stderr tail:\n" + "\n".join(log.splitlines()[-25:])
        )

    def test_omt_nav_plugin_loads(self):
        """Specifically assert omt_nav.ts (DEFECT A) loads cleanly via the
        default-plugin-function export."""
        log = _capture_serve(_free_port())
        failures = _failed_plugins(log)
        assert "omt_nav.ts" not in failures, (
            f"omt_nav.ts failed to load (DEFECT A regression):\n"
            f"  error: {failures.get('omt_nav.ts')}\n"
            f"stderr tail:\n" + "\n".join(log.splitlines()[-25:])
        )

    def test_pure_mode_loads_no_plugins(self):
        """Control: --pure runs opencode with no external plugins, so the log
        must contain NO `failed to load plugin` lines at all. This proves the
        failures above are caused by the OMT++ plugins, not the environment."""
        log = _capture_serve(_free_port(), pure=True)
        failures = _failed_plugins(log)
        assert not failures, (
            f"--pure mode still had plugin-load failures, so the failures above "
            f"are NOT caused by the OMT++ plugins (environment issue):\n"
            + "\n".join(f"  - {k}: {v}" for k, v in failures.items())
            + f"\nstderr tail:\n" + "\n".join(log.splitlines()[-25:])
        )
