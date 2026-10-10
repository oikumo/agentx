"""T3 gated-growth acceptance — propose/approve/reject/promote/prune + gates.

Hermetic (Tier-2): private per-module TOOLBOX_ROOT (``hermetic_cli``) — same
gates/assertions, zero real-toolbox writes, xdist-safe. No coverage loss.
"""
import json
import shutil
import sqlite3

from hermetic_toolbox import hermetic_cli  # noqa: F401  (pytest fixture)

E2E_ID = "text.probe_e2e"
REJECT_ID = "text.probe_reject"
GATE_ID = "text.probe_gate"


def db_state(root):
    db = root / "toolbox" / "index.sqlite3"
    con = sqlite3.connect(str(db))
    n_tools = con.execute("SELECT COUNT(*) FROM tools WHERE deprecated_by IS NULL").fetchone()[0]
    rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
    con.close()
    idx = json.loads((root / "toolbox" / "index.json").read_text())
    return n_tools, str(rev), str(idx["rev"])


def force_cleanup(root, tid):
    db = root / "toolbox" / "index.sqlite3"
    con = sqlite3.connect(str(db))
    con.execute("DELETE FROM tools WHERE id=?", (tid,))
    con.execute("DELETE FROM proposals WHERE id=?", (tid,))
    con.commit()
    con.close()
    name = tid.split(".", 1)[1] if "." in tid else tid
    cat = tid.split(".", 1)[0] if "." in tid else ""
    tdir = root / "toolbox" / cat / name
    if tdir.exists() and tdir.is_symlink() is False:
        shutil.rmtree(tdir)
    draft = root / ".sandbox" / "toolbox_proposals" / (tid.replace(".", "_") + ".md")
    if draft.exists():
        draft.unlink()
    tpath = root / "tests" / "scripts" / "toolbox" / f"test_{name}.py"
    if tpath.exists():
        tpath.unlink()


def test_reject_leaves_index_untouched(hermetic_cli):
    run_cli = hermetic_cli
    root = hermetic_cli.root
    force_cleanup(root, REJECT_ID)
    n0, rev0, _ = db_state(root)
    out = run_cli("propose", "--title", "probe reject", "--category", "text",
                  "--motive", "t3 reject-path test, 2 uses seen", "--uses-seen", "2")
    assert out.returncode == 0, out.stderr + out.stdout
    out = run_cli("reject", REJECT_ID, "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    payload = json.loads(out.stdout)
    assert payload["ok"] is True
    assert payload["data"]["status"] == "rejected"
    n1, rev1, _ = db_state(root)
    assert (n1, rev1) == (n0, rev0), "reject must leave tools+rev untouched"
    assert REJECT_ID not in [t["id"] for t in json.loads(run_cli("list", "--format", "json").stdout)["data"]]
    force_cleanup(root, REJECT_ID)


def test_promote_gate_rejects_low_uses(hermetic_cli):
    run_cli = hermetic_cli
    root = hermetic_cli.root
    force_cleanup(root, GATE_ID)
    assert run_cli("propose", "--title", "probe gate", "--category", "text",
                   "--motive", "t3 gate test, only 1 use", "--uses-seen", "1").returncode == 0
    assert run_cli("approve", GATE_ID).returncode == 0
    out = run_cli("promote", GATE_ID)
    assert out.returncode != 0, "promote must refuse <2 uses without general-use"
    assert ">=2" in out.stdout + out.stderr
    assert run_cli("reject", GATE_ID).returncode == 0
    force_cleanup(root, GATE_ID)


def test_propose_approve_promote_run_prune_cycle(hermetic_cli):
    run_cli = hermetic_cli
    root = hermetic_cli.root
    force_cleanup(root, E2E_ID)
    # propose + approve
    out = run_cli("propose", "--title", "probe e2e", "--category", "text",
                  "--motive", "t3 e2e pilot test, seen twice", "--uses-seen", "2",
                  "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    assert json.loads(out.stdout)["data"]["status"] == "staged"
    assert run_cli("approve", E2E_ID).returncode == 0
    # promote
    out = run_cli("promote", E2E_ID, "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    assert json.loads(out.stdout)["data"]["id"] == E2E_ID
    # run + query + lint
    out = run_cli("run", E2E_ID, env_extra={"TOOLBOX_SESSION": "test"})
    assert out.returncode == 0, out.stderr + out.stdout
    ids = [r["id"] for r in json.loads(run_cli("query", "probe e2e", "--format", "json").stdout)["data"]]
    assert E2E_ID in ids
    assert run_cli("lint").returncode == 0
    # prune deprecate -> query hides -> remove
    assert run_cli("prune", "--deprecate", E2E_ID, "--by", "text.json_split").returncode == 0
    ids = [r["id"] for r in json.loads(run_cli("query", "probe e2e", "--format", "json").stdout)["data"]]
    assert E2E_ID not in ids
    assert run_cli("prune", "--remove", E2E_ID).returncode == 0
    ids = [r["id"] for r in json.loads(run_cli("list", "--format", "json").stdout)["data"]]
    assert E2E_ID not in ids
    force_cleanup(root, E2E_ID)


def test_prune_reports_healthy(hermetic_cli):
    out = hermetic_cli("prune", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    payload = json.loads(out.stdout)
    assert payload["ok"] is True
    assert "candidates" in payload["data"] and "deprecated" in payload["data"]
