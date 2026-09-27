"""scripts/session_inspect — normalized OpenCode session evidence (feature_131).

One stdlib-only package owns source adapters, normalized records, labels,
hierarchy, and usage accounting for real OpenCode session logs. Slice-1
surface (design_001): schema · adapter · normalize · labels · hierarchy ·
usage · collect. Slice-2: query · inspect · trace · cli. Slice-3: profile ·
compare · exporter. Slice-4: manifest · evaluate (run gated unavailable). Read-only by contract (exports write only to explicit
destinations); every failure is a named Finding.
"""
