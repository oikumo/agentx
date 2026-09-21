# git.recent_log
- purpose: recent log (promoted: needed 2x this session: recent-log recipe for release notes and resume context).
- usage: `uv run scripts/toolbox/toolbox.py run git.recent_log`
- args: --lines N (default 10 for log; 5 generic).
- I/O: stdout JSON `{"ok":…, "data":…}`.
- example: query then run without forking ad-hoc bash.
- limits: read-only; uv-only; no push/fetch/clone; no *.env reads.
