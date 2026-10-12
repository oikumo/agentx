"""Frictionless startup composer — live-first, fail-closed (feature_162 O1/O2/O3)."""
from __future__ import annotations

def compose_startup(probe: dict, compiled: dict) -> dict:
    menu = (probe or {}).get('menu', {}) or {}
    live_next = menu.get('next', 'none')
    other = list(menu.get('other_enabled', []) or [])
    titles = dict(menu.get('titles', {}) or {})
    file_next = (compiled or {}).get('NEXT')
    stale = (file_next != live_next)
    obs = (probe or {}).get('observation', {}) or {}
    drifts = (probe or {}).get('drifts', 0)
    # O2 lean empty-pool: idle + nothing enabled + no drifts
    if obs.get('state') == 'idle_empty' and live_next in (None, 'none') and not other and not drifts:
        rev = (probe or {}).get('revision', 0)
        lines = [
            f"idle_empty rev{rev} — nothing live (stale file rev{(compiled or {}).get('net_rev','?')} ignored)",
            'capacity: workers/lanes/resources free',
            'R=reconcile | ?=detail',
        ]
        return {'letters': [], 'stale': bool(stale), 'lean': True, 'lines': lines}
    # live-first letters only (never stale file IDs)
    ids = [live_next] if live_next not in (None, 'none') else []
    for o in other:
        if o not in ids:
            ids.append(o)
    letters = []
    for i, oid in enumerate(ids):
        short = oid.split(':', 1)[1] if ':' in oid else oid
        title = titles.get(oid, '')
        # O3: never bare 001/002 — honest fallback when title missing
        if not title:
            title = f'{short} · scope unset' if short else oid
        letters.append({'letter': chr(ord('A') + i), 'id': oid, 'title': title})
    return {'letters': letters, 'stale': bool(stale), 'lean': False, 'lines': []}
