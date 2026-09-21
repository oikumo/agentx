# Proposal git.recent_log
- title: recent log
- category: git
- motive: needed 2x this session: recent-log recipe for release notes and resume context
- uses_seen: 2
created: 2026-09-21T12:52:00Z
- evidence: (1) motive cites recurring use; (2) uses_seen count in DB
- contract: `<cat>/<name>/run.sh` (set -euo pipefail, uv-only) + `main.py` (argparse, JSON) + `TOOL.md` (<=15 lines: purpose/usage/args/I-O/limits)
- denies: no push/fetch/clone, no bare python/pip/pytest, no *.env reads, no network
