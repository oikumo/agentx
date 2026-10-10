# agentx/ — product-only side of the split (sandbox demo)

Owner: product. Rule: no `meta` affix (e.g. `rag_v2`, `petri_net_studio`).

This folder is intentionally label-only: it proves the split is readable with
zero tooling changes. Real product homes live at `.projects/agentx/` (today a
single `META.md` placeholder with a **populated 4-row pending-moves draft** —
v3 wrongly called it "empty by design" — listing `agentx_concurrent_development`,
`rag_v2`, `petri_net_studio`, `agentx_1_0_0`, all still under `.projects/meta/`).

Put here (sandbox only): product notes, e.g. `rag_v2.md` (draft).
Never here: harness process, gates, `scripts/omt/` moves.

v4 note: readability ≠ enforceability — enforcement is T1 audit + T2 boundary
goldens (both deferred, import-statement regex with fixture-string + path-string
exemptions per PROPOSAL §0). Product-adjacent third leg `tools/petri-net-studio/`
(TS app, verified) is **recommended scoped as product** in T1 (see PROPOSAL §1/§8 Q2);
the two-home model alone doesn't cover it.
