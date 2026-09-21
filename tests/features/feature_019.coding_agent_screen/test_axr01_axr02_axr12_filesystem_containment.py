"""Durable regression proof for Package 1 filesystem containment (AXR-01/02/12).

Reconstructs the inline regression proof from
``sandbox/consistency_enforcement/round_002_package_01_filesystem_containment.md``
§Result (combo A1+B1+C1: ``mkstemp(dir=parent)`` O_EXCL + ``os.replace`` +
perm preserve in ``coding_tools.py``; search resolves+validates every rglob
result + 5-line preview cap; ``utils.py`` canonical resolve + explicit
containment, PermissionError contract kept) as durable tests.

Acceptance = the per-finding Regression checks in
``sandbox/consistency_enforcement/round_001_implementation_review.md``
§AXR-01/02/12 (AXR-01/02/12 share one path policy, PROJECT D5).

Probes retired, not gated (D4): the observation probes
``test_axr01_predictable_temp_symlink``,
``test_axr02_search_reads_outside_symlink`` and
``test_axr12_guard_accepts_traversal_and_symlink`` in
``sandbox/consistency_enforcement/round_001_review_probes.py`` asserted the
*faulty* behavior and must stop passing after the fix. The tests below assert
the *repaired* behavior and live under ``tests/``.

Hermetic: all paths under ``tmp_path``; no network (offline fixture); AXR-12
is guard-level only -- ``dangerous_delete_directory``/``shutil.rmtree`` are
never invoked on real dirs.
"""

from __future__ import annotations

import os
import socket
import tempfile

import pytest

# Import-time configuration only; must stay before application imports.
os.environ["PYTHON_DOTENV_DISABLED"] = "1"
os.environ["LLAMA_CPP_MODELS_CACHE_PATH"] = tempfile.gettempdir()
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refused(*args, **kwargs):
        raise AssertionError("Regression tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refused)
    monkeypatch.setattr(socket, "create_connection", refused)


def test_axr01_edit_ignores_preplanted_tmp_symlink(tmp_path, monkeypatch):
    """AXR-01: pre-planted ``<file>.tmp`` symlink must not divert the edit.

    Pre-create the old ``.tmp`` symlink, then verify the outside marker is
    unchanged, the final target is a regular file with the new content, and
    the edit reports success. The leftover ``.tmp`` symlink still existing
    proves the predictable name was never reused (fix:
    ``mkstemp(dir=validated_parent)`` O_EXCL + ``os.replace``).
    """
    from agentx.model.coding import coding_tools as coding

    root = tmp_path / "sandbox"
    root.mkdir()
    monkeypatch.setattr(coding, "_sandbox_root", root)
    target = root / "file.txt"
    target.write_text("old")
    target.chmod(0o640)
    expected_mode = target.stat().st_mode & 0o7777
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-before")
    (root / "file.txt.tmp").symlink_to(outside)

    result = coding._file_edit_impl("file.txt", "old", "new")

    assert result.success is True
    assert result.error is None
    assert outside.read_text() == "outside-before"
    assert not target.is_symlink()
    assert target.read_text() == "new"
    assert (target.stat().st_mode & 0o7777) == expected_mode
    # Predictable temp name never reused: the planted symlink is untouched.
    assert (root / "file.txt.tmp").is_symlink()


def test_axr02_search_excludes_outside_symlink(tmp_path, monkeypatch):
    """AXR-02: search must not leak outside-sandbox content via symlinks.

    An outside-pointing symlink in the tree is excluded from results (and
    direct read still rejects it) while a regular ``inner.txt`` is still
    found. Also pins the 5-line preview cap: a 20-line file yields at most
    5 context lines without a whole-file load.
    """
    from agentx.model.coding import coding_tools as coding

    root = tmp_path / "sandbox"
    root.mkdir()
    monkeypatch.setattr(coding, "_sandbox_root", root)
    outside = tmp_path / "outside.txt"
    outside.write_text("outside-sandbox-marker")
    (root / "link.txt").symlink_to(outside)
    (root / "inner.txt").write_text("inner-content")
    (root / "big.txt").write_text("\n".join(f"line-{i}" for i in range(20)))

    read_result = coding._file_read_impl("link.txt")
    assert read_result.error is not None
    assert "escapes sandbox" in read_result.error

    result = coding._file_search_impl("*.txt")

    assert result.error is None
    by_path = {m.path: m for m in result.matches}
    assert "inner.txt" in by_path
    assert "inner-content" in by_path["inner.txt"].context
    assert "link.txt" not in by_path
    assert all("outside-sandbox-marker" not in m.context for m in result.matches)
    assert len(by_path["big.txt"].context.splitlines()) <= 5


def test_axr12_guard_accepts_ordinary_child(tmp_path, monkeypatch):
    """AXR-12 (accept): an ordinary child of the allowlist is accepted."""
    from agentx.utils.utils import is_directory_allowed_to_deletion

    monkeypatch.chdir(tmp_path)
    allowed = tmp_path / "local_sessions"
    allowed.mkdir()
    child = allowed / "child"
    child.mkdir()

    assert is_directory_allowed_to_deletion(str(child)) is True


def test_axr12_guard_rejects_traversal_and_sibling_prefix(tmp_path, monkeypatch):
    """AXR-12 (reject): parent traversal and sibling-prefix paths raise.

    Contract preserved: rejection is ``PermissionError``, not a ``False``
    return. Guard-level only -- nothing is deleted.
    """
    from agentx.utils.utils import is_directory_allowed_to_deletion

    monkeypatch.chdir(tmp_path)
    allowed = tmp_path / "local_sessions"
    allowed.mkdir()
    (tmp_path / "unrelated").mkdir()

    with pytest.raises(PermissionError):
        is_directory_allowed_to_deletion(str(allowed / ".." / "unrelated"))
    with pytest.raises(PermissionError):
        is_directory_allowed_to_deletion(str(tmp_path / "local_sessions_suffix"))


def test_axr12_guard_rejects_outside_symlink(tmp_path, monkeypatch):
    """AXR-12 (reject): an allowlisted symlink pointing outside raises."""
    from agentx.utils.utils import is_directory_allowed_to_deletion

    monkeypatch.chdir(tmp_path)
    allowed = tmp_path / "local_sessions"
    allowed.mkdir()
    outside = tmp_path / "unrelated"
    outside.mkdir()
    (allowed / "link").symlink_to(outside, target_is_directory=True)

    with pytest.raises(PermissionError):
        is_directory_allowed_to_deletion(str(allowed / "link"))
