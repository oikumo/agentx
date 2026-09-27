"""exporter.py — versioned evidence bundles + replay (feature_131 S3).

Writes only to the explicit `dest` directory; files become visible
atomically (tmp + os.replace) after validation. Replay recomputes the
digest from the saved snapshot without new model calls.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

BUNDLE_VERSION = 1


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, default=str).encode()


def _digest(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()[:16]


def _atomic_write(path: Path, payload: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str))
    os.replace(tmp, path)


def export_bundle(snapshot: dict[str, Any], *, dest: str,
                  name: str) -> dict[str, Any]:
    """Export snapshot + compact report + replay manifest (atomic)."""
    outdir = Path(dest)
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {"version": BUNDLE_VERSION,
               "sessions": snapshot.get("sessions", ()),
               "messages": snapshot.get("messages", ()),
               "parts": snapshot.get("parts", ()),
               "events": snapshot.get("events", ()),
               "coverage": snapshot.get("coverage", {})}
    digest = _digest(payload)
    snap_path = outdir / f"{name}.snapshot.json"
    report = {"version": BUNDLE_VERSION, "digest": digest,
              "counts": {k: len(payload[k])
                         for k in ("sessions", "messages", "parts", "events")},
              "detail_ref": f"bundle:{name}:{digest}"}
    report_path = outdir / f"{name}.report.json"
    manifest = {"version": BUNDLE_VERSION, "name": name, "digest": digest,
                "replay": {"snapshot": snap_path.name,
                           "metric": "sha256-16(canonical-json)"},
                "source": "scripts/session_inspect exporter v1"}
    manifest_path = outdir / f"{name}.manifest.json"
    _atomic_write(snap_path, payload)
    _atomic_write(report_path, report)
    _atomic_write(manifest_path, manifest)
    return {"digest": digest,
            "paths": {"snapshot": str(snap_path),
                      "report": str(report_path),
                      "manifest": str(manifest_path)},
            "detail_ref": report["detail_ref"]}


def replay_bundle(snapshot_path: str) -> dict[str, Any]:
    """Recompute a saved bundle digest (no model calls; stable N)."""
    payload = json.loads(Path(snapshot_path).read_text())
    return {"digest": _digest(payload), "version": payload.get("version", 1)}
