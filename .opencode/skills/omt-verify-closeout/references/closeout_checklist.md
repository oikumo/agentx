# Closeout checklist (references, policy by reference — OMT is authority)

- [ ] Docs: FEATURE.md + analysis/design/impl/test_report exist for the slug.
- [ ] Doctor: `skill.py doctor` green on related skills.
- [ ] Goldens: feature test dir green via subprocess (no full suite).
- [ ] WORK: size within budget (`test_work_md_within_budget`).
- [ ] TDD: `tdd done` claim present in test_report (no new failures vs baseline).
- [ ] Split_proof: 39/39 claim present (CI owns re-run, skill checks the claim).

Envelope: verified→succeeded/OK; blocked→failed check + remediation; not_applicable→unknown slug; inconclusive→conflicting evidence.
