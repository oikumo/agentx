# Impl 001 — wire-in (feature_163)

- .opencode/plugins/startup_table.ts renderTables: live-first IDs (probe next/other_enabled, bare->unscoped:), lean branch on live-empty (zero stale letters), titles in rows, S prefers live target. Non-harness file, no registry churn. bun build OK.
- .meta/META_HARNESS.omt @doc startup: live-first lean rule (519B, was 772B) + harnessc build -> AGENTS.md. Budgets held (work_md trim on 152 Next).
- Effortless: hi+empty -> <=3 lines, 1 probe; history via logc --last.
