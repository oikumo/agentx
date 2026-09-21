# text.json_split
- purpose: split JSON-array or bullet/newline behaviors (rehomed tdd recipe).
- usage: `uv run scripts/toolbox/toolbox.py run text.json_split -- --text "[\"a\"]"`
- args: --text TEXT (JSON array or prose).
- I/O: stdout JSON `{"ok":true, "data":{"behaviors":[…]}}`.
- example: testlist prose without re-typing the splitter.
- limits: read-only; no writes; no network.
