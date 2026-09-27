"""RED 6 — end-to-end collect pipeline (op_spec_001 `collect.py`).

Mini-matrix labeled fixture DB: 2 variants x 2 cases x 2 reps = 8 trials,
one trial missing its end event, one echo, one orphan span. collect_trials
must bind labels to exactly the usable trial set with per-trial usage,
exclusion reasons, and named findings — echoes never mint trials.
"""
import json

from conftest import build_db, msg_row, part_row, ses_row

V1 = "[mh13.experiment]"


def lbl(**kw):
    return V1 + " " + json.dumps(kw)


def trial_lines(case, variant, rep, *, complete=True):
    trial = f"{case}_{variant}_rep{rep}"
    start = lbl(v=1, experiment="context_strategy", run="run_001", trial=trial,
                case=case, variant=variant, rep=rep, attempt=1,
                event="trial_start")
    if not complete:
        return start
    end = lbl(v=1, run="run_001", trial=trial, attempt=1,
              event="trial_end", outcome="completed")
    return start + "\n" + end


def _collect():
    from session_inspect import collect
    return collect


def _build_fixture(tmp_path):
    sessions, messages, parts = [], [], []
    n = 0
    for case in ("case01", "case02"):
        for variant in ("baseline", "kernel"):
            for rep in (1, 2):
                n += 1
                sid = f"ses_t{n}"
                complete = not (case == "case02" and variant == "kernel" and rep == 2)
                sessions.append(ses_row(
                    sid, parent_id="ses_root", title=f"trial {case}/{variant}/{rep}",
                    time_created=1790000000000 + n,
                    ti=100 * n, to=10 * n, tr=0, tcr=1000 * n))
                mid = f"msg_{sid}"
                messages.append(msg_row(mid, sid, role="user",
                                       time_created=1790000000000 + n))
                parts.append(part_row(f"p_{sid}", mid, sid, ptype="text",
                                       payload={"text": trial_lines(
                                           case, variant, rep, complete=complete)},
                                       time_created=1790000000000 + n))

    # root session (unlabeled parent)
    sessions.append(ses_row("ses_root", time_created=1790000000000))

    # echo: label text inside an ASSISTANT tool output — never a trial
    sessions.append(ses_row("ses_echo", time_created=1790000900000))
    messages.append(msg_row("msg_e", "ses_echo", role="assistant",
                            time_created=1790000900000))
    parts.append(part_row("p_e", "msg_e", "ses_echo", ptype="tool",
                         payload={"tool": "bash",
                                  "state": {"status": "completed",
                                            "output": trial_lines("case01",
                                                                  "baseline",
                                                                  1)}},
                         time_created=1790000900000))

    # orphan: span_end without any established trial
    sessions.append(ses_row("ses_orphan", time_created=1790000950000))
    mid = "msg_o"
    messages.append(msg_row(mid, "ses_orphan", role="user",
                           time_created=1790000950000))
    parts.append(part_row("p_o", mid, "ses_orphan", ptype="text",
                         payload={"text": lbl(
                             v=1, run="run_001", trial="ghost", attempt=1,
                             event="span_end", span="s")},
                         time_created=1790000950000))

    return build_db(tmp_path / "matrix.db", sessions=sessions,
                    messages=messages, parts=parts)


def test_collect_trials_end_to_end(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector

    db = _build_fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    report = _collect().collect_trials(ad, SessionSelector(directory="/repo"))

    assert len(report.trials) == 8  # 2 variants x 2 cases x 2 reps
    names = [f.name for f in report.findings]
    assert "echo_not_trial" in names       # tool-output echo recorded
    assert "label_orphan_event" in names   # orphan span_end recorded

    # the incomplete trial (missing trial_end) is excluded with a reason
    incomplete_key = "case02_kernel_rep2"
    entry = report.trials[incomplete_key]
    assert entry.usable is False
    assert "trial_incomplete" in entry.exclusions

    # all 7 others usable, bound to exactly one session, with usage
    usable = {k: e for k, e in report.trials.items() if e.usable}
    assert len(usable) == 7
    for k, e in report.trials.items():
        assert len(e.session_ids) == 1, k
        if e.usable:
            assert e.usage is not None and e.outcome == "completed", k

    # per-trial usage = session cumulative counters of the bound session
    base = report.trials["case01_baseline_rep1"]
    assert base.usage["input"] == 100      # ses_t1 ti=100*1
    assert base.usage["cache_read"] == 1000

    # echoes minted no trial: the echoed label identity resolves to an
    # existing trial (case01_baseline_rep1) and must NOT rebind or duplicate
    assert len(report.trials["case01_baseline_rep1"].session_ids) == 1

    # coverage: every session in the selection is accounted for
    assert report.coverage["n_sessions"] == 11  # 8 + root + echo + orphan
    assert report.coverage["n_labeled_sessions"] == 8
