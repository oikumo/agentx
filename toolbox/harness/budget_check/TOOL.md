# harness.budget_check
- purpose: wrap harnessc check budgets (rehomed recipe).
- usage: `uv run scripts/toolbox/toolbox.py run harness.budget_check`
- args: none (read-only).
- I/O: stdout JSON `{"ok":…, "data":{"rc":…, "tail":[…]}}`.
- example: budgets green check without remembering flags.
- limits: read-only; uv-only; no network.
