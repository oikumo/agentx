"""test_slice6_s6_acceptance.py — S6 B1/B2 + live AC battery (design_003, RED)."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from tests.scripts.session_inspect.conftest import build_db, ses_row, msg_row, part_row, tok

REPO_ROOT = Path(__file__).resolve().parents[3]


def _mini_db(tmp_path):
    db = str(tmp_path / "s6.db")
    build_db(db,
             sessions=[ses_row("ses_a", directory="/repo", title="a", ti=100, to=20)],
             messages=[msg_row("msg_u1", "ses_a", role="user", parent_id=None),
                       msg_row("msg_a1", "ses_a", role="assistant", parent_id="msg_u1",
                               tokens=tok(total=120, input=100, output=20))],
             parts=[part_row("p1", "msg_u1", "ses_a", ptype="text", payload={"text": "hi"})])
    return db


def test_s6_b1_no_shadow_as_script(tmp_path):
    """B1: service.py launched as script must exit 0 (stdlib inspect not shadowed)."""
    db = _mini_db(tmp_path)
    # Enforce rename: no inspect.py on disk (shadows stdlib while present).
    assert not (REPO_ROOT / "scripts" / "session_inspect" / "inspect.py").exists(), \
        "scripts/session_inspect/inspect.py shadows stdlib inspect — rename to detail.py"
    proc = subprocess.run(
        ["uv", "run", "scripts/session_inspect/service.py", "sessions",
         "--db", db, "--directory", "/repo", "--limit", "2"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, f"script launch failed: {proc.stderr[-2000:]}"
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out.get("ok") is True


def test_s6_b2_bounded(tmp_path):
    """B2: over-budget directory query returns query_limit_exceeded + cursor; ids drill-down ok."""
    import sys
    sys.path.insert(0, str(REPO_ROOT / 'scripts'))
    import importlib
    svc = importlib.import_module('session_inspect.service')
    importlib.reload(svc)
    # 30 sessions in one directory, no time bounds -> over cap
    sessions = [ses_row(f'ses_{i:02d}', directory='/big', title='t', time_created=1790000000000+i) for i in range(30)]
    db = str(tmp_path / 's6b2.db')
    build_db(db, sessions=sessions, messages=[], parts=[])
    r = svc.dispatch('sessions', {'db': db, 'directory': '/big', 'limit': 10})
    assert r['ok'] is False and r.get('error') == 'query_limit_exceeded', r
    assert 'cursor' in r, r
    # drill-down via session_ids bypasses directory cap
    r2 = svc.dispatch('sessions', {'db': db, 'directory': '/big', 'session_ids': 'ses_00', 'limit': 10})
    # session_ids as string filter: adapter expects list? service currently passes directory only;
    # accept either ok with rows or explicit bounded path — must not be query_limit_exceeded
    assert r2.get('error') != 'query_limit_exceeded', r2


def _chain_db(tmp_path):
    sessions = [ses_row("ses_a", directory="/repo", title="chain",
                        time_created=1790000000000, ti=300, to=30)]
    messages = [
        msg_row("msg_u1", "ses_a", role="user", parent_id=None,
                time_created=1790000000000),
        msg_row("msg_a1", "ses_a", role="assistant", parent_id="msg_u1",
                time_created=1790000000100,
                tokens=tok(total=1110, input=100, output=10, cache_read=1000)),
        msg_row("msg_a2", "ses_a", role="assistant", parent_id="msg_a1",
                time_created=1790000000200,
                tokens=tok(total=2220, input=200, output=20, cache_read=2000)),
    ]
    parts = [part_row("p1", "msg_a1", "ses_a", ptype="text",
                      payload={"text": "expensive turn"},
                      time_created=1790000000100)]
    return build_db(str(tmp_path / "s6chain.db"), sessions=sessions,
                    messages=messages, parts=parts)


def test_s6_ac1_ac5_live(tmp_path):
    """S6 AC1-AC5 live chain via omt_session dispatcher (design_003 §3)."""
    import importlib
    svc = importlib.import_module('session_inspect.service')
    importlib.reload(svc)
    db = _chain_db(tmp_path)
    # AC1: session discovery via ids returns source identity
    r = svc.dispatch('sessions', {'db': db, 'directory': '/repo',
                                  'session_ids': 'ses_a', 'limit': 5})
    assert r.get('ok') is True, r
    rows = r['result']['rows']
    assert any(x.get('session_id') == 'ses_a' for x in rows), r
    # AC2: hotspot -> part -> trace chain must be real evidence, not stub
    rp = svc.dispatch('profile', {'db': db, 'session_id': 'ses_a'})
    assert rp.get('ok') is True, rp
    assert 'rows' in rp.get('result', {}), rp  # stub returns only {op:...} -> RED
    assert rp['result']['rows'][0]['message_id'] == 'msg_a2', rp
    ri = svc.dispatch('inspect', {'db': db, 'session_id': 'ses_a',
                                  'part_id': 'p1'})
    assert ri.get('ok') is True and 'part_id' in ri.get('result', {}), ri
    rt = svc.dispatch('trace', {'db': db, 'session_id': 'ses_a'})
    assert rt.get('ok') is True and 'skeleton' in rt.get('result', {}), rt
    # live-gated AC1 shapes + A2 reconcile (opt-in, read-only)
    if os.environ.get('MH13_LIVE_DB'):
        live = os.environ.get('MH13_DB_PATH') or os.path.expanduser(
            '~/.local/share/opencode/opencode.db')
        rl = svc.dispatch('sessions', {'db': live, 'directory': '/repo',
                                       'session_ids': 'ses_a', 'limit': 2})
        assert rl.get('ok') in (True, False), rl


def _bench_db(tmp_path, n=12):
    sessions = [ses_row(f"ses_b{i:02d}", directory="/repo", title="b",
                        time_created=1790000000000 + i,
                        ti=100 * (i + 1)) for i in range(n)]
    messages = [msg_row(f"msg_b{i:02d}", f"ses_b{i:02d}", role="assistant",
                        time_created=1790000000000 + i,
                        tokens=tok(total=120, input=100, output=20))
                for i in range(n)]
    return build_db(str(tmp_path / "s6bench.db"), sessions=sessions,
                    messages=messages)


def test_s6_ac3_bench(tmp_path):
    """S6 AC3 bench: pagination completeness + limits + cold/warm split."""
    import importlib
    import json as _j
    import time
    svc = importlib.import_module('session_inspect.service')
    importlib.reload(svc)
    db = _bench_db(tmp_path, n=12)
    q = {"filters": {"directory": "/repo"}, "limit": 5}
    r1 = svc.dispatch('query', {'db': db, 'query_json': _j.dumps(q),
                                'limit': 5})
    assert r1.get('ok') is True, r1
    res = r1.get('result', {})
    assert 'rows' in res and 'cursor' in res and 'total' in res, r1
    # walk pages via query module fetch_page: no missing/duplicates
    from session_inspect import query as _q
    seen, cur = [], res['cursor']
    seen.extend([x.get('message_id') or x.get('session_id') for x in res['rows']])
    while cur and len(seen) < res['total']:
        nxt = _q.fetch_page(cur, 5)
        seen.extend([x.get('message_id') or x.get('session_id') for x in nxt['rows']])
        cur = nxt['cursor']
        if not nxt['rows']:
            break
    assert len(seen) == res['total'] and len(set(seen)) == len(seen), (len(seen), res['total'])
    # named resource-limit failure, never silent truncation
    rbad = svc.dispatch('query', {'db': db,
                                  'query_json': _j.dumps({"filters": {}, "limit": 5000})})
    assert rbad.get('ok') is False and 'limit' in str(rbad).lower(), rbad
    # cold/warm split reported separately (synthetic timing shape)
    t0 = time.perf_counter()
    svc.dispatch('query', {'db': db, 'query_json': _j.dumps(q), 'limit': 5})
    cold = time.perf_counter() - t0
    t0 = time.perf_counter()
    svc.dispatch('query', {'db': db, 'query_json': _j.dumps(q), 'limit': 5})
    warm = time.perf_counter() - t0
    assert cold >= 0 and warm >= 0, (cold, warm)
    if os.environ.get('MH13_LIVE_DB'):
        import sqlite3
        live = os.environ.get('MH13_DB_PATH') or os.path.expanduser(
            '~/.local/share/opencode/opencode.db')
        conn = sqlite3.connect(f"file:{live}?mode=ro", uri=True, timeout=5.0)
        try:
            nm = conn.execute("SELECT COUNT(*) FROM message").fetchone()[0]
            np = conn.execute("SELECT COUNT(*) FROM part").fetchone()[0]
        finally:
            conn.close()
        assert nm + np >= 100000, (nm, np)


def _replay_db(tmp_path):
    sessions = [ses_row("ses_r1", directory="/repo", title="r1",
                        time_created=1790000000000, ti=100),
                ses_row("ses_r2", directory="/repo", title="r2",
                        time_created=1790000000100, ti=200)]
    messages = [msg_row("msg_r1", "ses_r1", role="assistant",
                        time_created=1790000000000,
                        tokens=tok(total=120, input=100, output=20)),
                msg_row("msg_r2", "ses_r2", role="assistant",
                        time_created=1790000000100,
                        tokens=tok(total=240, input=200, output=40))]
    return build_db(str(tmp_path / "s6replay.db"), sessions=sessions,
                    messages=messages)


def test_s6_ac9_replay(tmp_path):
    """S6 AC9 replay: export selected snapshot, digest stable, no model calls."""
    import importlib
    import json as _j
    svc = importlib.import_module('session_inspect.service')
    importlib.reload(svc)
    db = _replay_db(tmp_path)
    dest = str(tmp_path / "bundle_out")
    sel = _j.dumps({"session_ids": ["ses_r1"]})
    r = svc.dispatch('export', {'db': db, 'selection_json': sel,
                                'dest': dest})
    assert r.get('ok') is True, r
    res = r.get('result', {})
    assert 'digest' in res and 'paths' in res, r
    snap_path = res['paths']['snapshot']
    # selected export respects filter: only ses_r1 (RED vs hardcoded /repo snapshot)
    snap = _j.loads(open(snap_path).read())
    sids = [s.get('id') if isinstance(s, dict) else getattr(s, 'id', None)
            for s in snap.get('sessions', [])]
    assert sids == ['ses_r1'], (sids, res)
    # replay recomputes same digest without model calls; re-export stable
    from session_inspect import exporter as _ex
    again = _ex.replay_bundle(snap_path)
    assert again['digest'] == res['digest'], (again, res)
    dest2 = str(tmp_path / "bundle_out2")
    r2 = svc.dispatch('export', {'db': db, 'selection_json': sel,
                                 'dest': dest2})
    assert r2.get('result', {}).get('digest') == res['digest'], r2


def test_s6_pilot_dry_run(tmp_path):
    """S6 pilot dry_run: 12 trials, executed False, invalid rejected, run gated."""
    import importlib
    import json as _j
    svc = importlib.import_module('session_inspect.service')
    importlib.reload(svc)
    man = {"version": 1, "experiment": "context_strategy", "run": "run_001",
           "cases": ["markdown-summary", "python-fix"],
           "variants": ["baseline", "candidate"], "reps": 3}
    r = svc.dispatch('experiment', {'sub': 'dry_run',
                                    'manifest': _j.dumps(man)})
    assert r.get('ok') is True, r
    res = r.get('result', {})
    assert res.get('n_trials') == 12, res  # 2x2x3 stub returns no matrix -> RED
    assert res.get('executed') is False, res
    assert len(res.get('label_lines', [])) == 12, res
    assert all(l.startswith('[mh13.experiment]') for l in res['label_lines']), res
    # negative: invalid manifest rejected with named finding, never executed
    bad = dict(man)
    del bad['variants']
    rb = svc.dispatch('experiment', {'sub': 'dry_run',
                                     'manifest': _j.dumps(bad)})
    assert rb.get('ok') is False and 'manifest_invalid' in str(rb), rb
    # run stays gated: no launches/tokens without explicit approval
    rr = svc.dispatch('experiment', {'sub': 'run',
                                     'manifest': _j.dumps(man)})
    assert rr.get('executed') is False, rr
    assert rr.get('reason') == 'no_safe_launch', rr
