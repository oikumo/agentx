"""RED S4 — manifest contract + dry run (design_001 S4)."""


def test_manifest_contract():
    from session_inspect import manifest
    m = manifest.create(experiment="context_strategy", run="run_001",
                        cases=["case01", "case02"],
                        variants=["baseline", "candidate"], reps=3)
    assert manifest.validate(m)["ok"] is True
    assert m["version"] == 1
    bad = dict(m)
    del bad["variants"]
    try:
        manifest.validate(bad)
        assert False, "missing variants must fail"
    except Exception as exc:
        assert "manifest_invalid" in str(exc)


def test_manifest_dry_run():
    from session_inspect import manifest
    m = manifest.create(experiment="ctx", run="run_001",
                        cases=["case01"], variants=["baseline", "candidate"],
                        reps=2)
    plan = manifest.dry_run(m)
    assert plan["n_trials"] == 4
    assert all(l.startswith("[mh13.experiment]") for l in plan["label_lines"])
    assert plan["executed"] is False
