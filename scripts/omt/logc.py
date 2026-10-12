"""Git-log state compiler — O6 (feature_162). 1 call, zero reasoning."""
from __future__ import annotations
import json, subprocess

def _sh(*a: str) -> str:
    try:
        return subprocess.run(list(a), capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ''

def last_state() -> dict:
    head = _sh('git', 'log', '-1', '--format=%H %s')
    subject = head.split(' ', 1)[1] if ' ' in head else head
    projects = _sh('git', 'log', '-8', '--format=%s')
    return {'head_subject': subject or 'none', 'projects': [l for l in projects.splitlines() if l][:8]}

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--last', action='store_true')
    a = ap.parse_args()
    if a.last:
        print(json.dumps(last_state(), indent=1))
