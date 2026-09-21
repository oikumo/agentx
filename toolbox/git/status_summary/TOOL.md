# git.status_summary
- purpose: porcelain git status + branch (rehomed recipe).
- usage: `uv run scripts/toolbox/toolbox.py run git.status_summary`
- args: none (read-only).
- I/O: stdout JSON `{"ok":…, "data":{"status":…}}`.
- example: dirty list without forking ad-hoc bash.
- limits: no push/fetch/clone; read-only; no *.env reads.
