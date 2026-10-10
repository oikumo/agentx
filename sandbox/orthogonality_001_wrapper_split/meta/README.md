# meta/ — harness-only side of the split (sandbox demo)

Owner: harness. Rule: new items end `*_meta`. Legacy `meta_*` grandfathered.

This folder is intentionally label-only: it proves the split is readable with
zero tooling changes. Real harness homes live at `.projects/meta/` (25 entries:
24 projects + `META.md` GENERATED, verified 2026-10-10).

Put here (sandbox only): harness notes, e.g. `net_gate_meta.md` (draft).
Never here: product code, product tests, `src/` moves.

v4 note: real harness code lives scattered (`scripts/omt/` 13 CLIs,
`scripts/session_inspect/`, `.meta/` (7 files in `.meta/.omt/`),
`.opencode/plugins/` 11 files for 14 tools + `.opencode/lib/enforcer/` ×12)
— there is no top-level `harness/` to rename; rename-away proofs must list the
four dirs explicitly (see PROPOSAL §7 / UC1). Net subsystem is 20 `.py` files
(v3 listed only the 6-file gate slice) + `META_NET.petri.json` + `supervisor.overlay`.
