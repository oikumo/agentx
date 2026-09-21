# session.pause_note_append
- purpose: stage pause-note entry (rehomed pause workflow).
- usage: `uv run scripts/toolbox/toolbox.py run session.pause_note_append -- --note "…"`.
- args: --note TEXT, --write (writes only to .sandbox/toolbox_runs/).
- I/O: stdout JSON `{"ok":…, "data":{"dry_run":…}}`.
- example: pause context without hand-rolled echo.
- limits: no writes outside .sandbox/toolbox_runs; dry-run default.
