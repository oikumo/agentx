# ledger.window_slice
- purpose: tail-slice ledger.jsonl (rehomed WORK.md recipe).
- usage: `uv run scripts/toolbox/toolbox.py run ledger.window_slice -- --lines 5`
- args: --lines N (default 5), --kind KIND (optional filter).
- I/O: stdout JSON `{"ok":…, "data":{"total":…, "slice":[…]}}`.
- example: last 5 completions without hand-rolled tail.
- limits: read-only; no writes; no *.env reads.
