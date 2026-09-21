"""T3 gated-growth acceptance — propose/approve/reject/promote/prune + gates."""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLI = [sys.executable, str(ROOT / "scripts" / "toolbox" / "toolbox.py")]
DB = ROOT / "toolbox" / "index.sqlite3"

E2E_ID = "text.probe_e2e"
REJECT_ID = "text.probe_reject"
GATE_ID = "text.probe_gate"


def run_cli(*args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    out = subprocess.run([*CLI, *args], capture_output=True, text=True, timeout=120, env=env)
    return out


def db_state():
    con = sqlite3.connect(str(DB))
    n_tools = con.execute("SELECT COUNT(*) FROM tools WHERE deprecated_by IS NULL").fetchone()[0]
    rev = con.execute("SELECT v FROM toolbox_meta WHERE k='rev'").fetchone()[0]
    con.close()
    idx = json.loads((ROOT / "toolbox" / "index.json").read_text())
    return n_tools, str(rev), str(idx["rev"])


def force_cleanup(tid):
    con = sqlite3.connect(str(DB))
    con.execute("DELETE FROM tools WHERE id=?", (tid,))
    con.execute("DELETE FROM proposals WHERE id=?", (tid,))
    con.commit()
    con.close()
    name = tid.split(".", 1)[1] if "." in tid else tid
    cat = tid.split(".", 1)[0] if "." in tid else ""
    tdir = ROOT / "toolbox" / cat / name
    import shutil
    if tdir.exists():
        shutil.rmtree(tdir)
    draft = ROOT / ".sandbox" / "toolbox_proposals" / (tid.replace(".", "_") + ".md")
    if draft.exists():
        draft.unlink()
    tpath = ROOT / "tests" / "scripts" / "toolbox" / f"test_{name}.py"
    if tpath.exists():
        tpath.unlink()


def test_reject_leaves_index_untouched():
    force_cleanup(REJECT_ID)
    n0, rev0, _ = db_state()
    out = run_cli("propose", "--title", "probe reject", "--category", "text",
                  "--motive", "t3 reject-path test, 2 uses seen", "--uses-seen", "2")
    assert out.returncode == 0, out.stderr + out.stdout
    out = run_cli("reject", REJECT_ID, "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    payload = json.loads(out.stdout)
    assert payload["ok"] is True
    assert payload["data"]["status"] == "rejected"
    n1, rev1, _ = db_state()
    assert (n1, rev1) == (n0, rev0), "reject must leave tools+rev untouched"
    assert REJECT_ID not in [t["id"] for t in json.loads(run_cli("list", "--format", "json").stdout)["data"]]
    force_cleanup(REJECT_ID)


def test_promote_gate_rejects_low_uses():
    force_cleanup(GATE_ID)
    assert run_cli("propose", "--title", "probe gate", "--category", "text",
                   "--motive", "t3 gate test, only 1 use", "--uses-seen", "1").returncode == 0
    assert run_cli("approve", GATE_ID).returncode == 0
    out = run_cli("promote", GATE_ID)
    assert out.returncode != 0, "promote must refuse <2 uses without general-use"
    assert ">=2" in out.stdout + out.stderr
    assert run_cli("reject", GATE_ID).returncode == 0
    force_cleanup(GATE_ID)


def test_propose_approve_promote_run_prune_cycle():
    force_cleanup(E2E_ID)
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
    force_cleanup(E2E_ID)


def test_prune_reports_healthy():
    out = run_cli("prune", "--format", "json")
    assert out.returncode == 0, out.stderr + out.stdout
    payload = json.loads(out.stdout)
    assert payload["ok"] is True
    assert "candidates" in payload["data"] and "deprecated" in payload["data"]
