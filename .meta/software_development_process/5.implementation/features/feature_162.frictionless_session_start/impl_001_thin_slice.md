# Impl 001 — thin slice (feature_162)

- scripts/omt/startupc.py compose_startup(probe, compiled): live-first, fail-closed (O1), lean <=3 lines when idle_empty+no drifts (O2), titles with honest fallback (O3).
- scripts/omt/logc.py last_state() + --last: git log -1 subject + last 8 subjects as projects (O6 compiler, 1 call).
- Effortless: 1 probe + 1 logc call, no WORK.md hunts, no stale letters.
