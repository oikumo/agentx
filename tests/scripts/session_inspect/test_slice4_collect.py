"""RED S4 — manifest-bound collection validation (design_001 S4)."""
import json

from conftest import build_db, msg_row, part_row, ses_row

V1 = "[mh13.experiment]"


def lbl(**kw):
    return V1 + " " + json.dumps(kw)


def trial_lines(case, variant, rep, *, complete=True):
    trial = f"{case}_{variant}_rep{rep:02d}"
    start = lbl(v=1, experiment="ctx", run="run_001", trial=trial,
                case=case, variant=variant, rep=rep, attempt=1,
                event="trial_start")
    if not complete:
        return start
    end = lbl(v=1, run="run_001", trial=trial, attempt=1,
              event="trial_end", outcome="completed")
    return start + "\n" + end


def _fixture(tmp_path):
    sessions, messages, parts = [], [], []
    n = 0
    for case in ("case01", "case02"):
        for variant in ("baseline", "candidate"):
            n += 1
            sid = f"ses_{n}"
            complete = not (case == "case02" and variant == "candidate")
            sessions.append(ses_row(sid, time_created=1790000000000 + n,
                                    ti=100 * n))
            mid = f"msg_{sid}"
            messages.append(msg_row(mid, sid, role="user",
                                    time_created=1790000000000 + n))
            parts.append(part_row(f"p_{sid}", mid, sid, ptype="text",
                                  payload={"text": trial_lines(
                                      case, variant, 1,
                                      complete=complete)},
                                  time_created=1790000000000 + n))
    return build_db(tmp_path / "m.db", sessions=sessions,
                     messages=messages, parts=parts)


def test_collect_binding(tmp_path):
    from session_inspect.adapter import OpenCodeSqliteAdapter, SessionSelector
    from session_inspect import collect, evaluate, manifest
    db = _fixture(tmp_path)
    ad = OpenCodeSqliteAdapter(db)
    m = manifest.create(experiment="ctx", run="run_001",
                        cases=["case01", "case02"],
                        variants=["baseline", "candidate"], reps=1)
    report = collect.collect_trials(ad, SessionSelector(directory="/repo"))
    verdict = evaluate.validate_collection(m, report)
    assert verdict["n_expected"] == 4
    assert verdict["n_usable"] == 3
    assert verdict["incomplete"] == ["case02_candidate_rep01"]
    assert verdict["n_independent"] == 3
