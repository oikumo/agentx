"""RED: frictionless startup — O1/O2/O3/O6 effortless (feature_162)."""


def test_o1_live_first_no_stale_picks():
    probe = {"revision": 0, "observation": {"state": "idle_empty"},
             "menu": {"next": "none", "other_enabled": []}}
    compiled = {"net_rev": 60, "NEXT": "proj:agentx_concurrent_development",
                "OptionIDs": ["proj:agentx_concurrent_development", "unscoped:001"]}
    from scripts.omt.startupc import compose_startup
    out = compose_startup(probe, compiled)
    assert out["letters"] == []
    assert out["stale"] is True


def test_o2_lean_empty_pool():
    probe = {"revision": 0, "observation": {"state": "idle_empty"},
             "menu": {"next": "none", "other_enabled": []}, "drifts": 0}
    from scripts.omt.startupc import compose_startup
    out = compose_startup(probe, {"net_rev": 60, "NEXT": "x", "OptionIDs": []})
    assert out["lean"] is True
    assert len(out["lines"]) <= 3


def test_o3_titles_resolved():
    probe = {"revision": 1, "observation": {"state": "busy"},
             "menu": {"next": "unscoped:001", "other_enabled": ["unscoped:001"],
                      "titles": {"unscoped:001": "feature_001 session objectives"}}}
    from scripts.omt.startupc import compose_startup
    out = compose_startup(probe, {"net_rev": 1, "NEXT": "unscoped:001", "OptionIDs": ["unscoped:001"]})
    assert out["letters"][0]["title"] != "001"


def test_o6_logc_last_state():
    from scripts.omt.logc import last_state
    st = last_state()
    assert "head_subject" in st and "projects" in st
