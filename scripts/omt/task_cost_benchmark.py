#!/usr/bin/env python3
"""Task-cost benchmark shim (feature_093.task_cost_benchmark).

Delegates to scripts/omt/bench/cli.py — kept as a top-level shim so the
benchmark is invocable as `uv run scripts/omt/task_cost_benchmark.py ...`
like the other tdd/net shims.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
