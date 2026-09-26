# toolbox onboarding (GENERATED snippet)

toolbox: 6 tools rev=38 - query: toolbox.py query "..."

## Discover in <=2 calls
1. `uv run scripts/toolbox/toolbox.py query "<keywords>"` (add `--tier 1` for core-5 only)
2. `uv run scripts/toolbox/toolbox.py show <id>` then `run <id> -- --help`

## Tiers
- Tier-1 (minimal): core-5 rehomed seeds — git.status_summary, ledger.window_slice,
  harness.budget_check, text.json_split, session.pause_note_append.
- Tier-2/3 (full): all non-deprecated tools incl. promoted (see `tiers`).

## Grow / prune
- encounter 2x (or 1x general-use) -> `propose` (staged) -> approve -> `promote` -> `run` metered.
- `stats` shows uses/successes; `prune` deprecates uses==0 >90d (one-cycle warning).

> rev=38 tools=6 categories=5 — regen: `toolbox.py docs --gen`, check: `docs --check`.
