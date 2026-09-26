"""Reason SSOT — elaborator (stdlib only, advisory, no harness writes)."""
import json
import hashlib
from pathlib import Path

SB = Path(__file__).resolve().parents[2] / ".sandbox" / "harness_reason"


def _load_text(source: str) -> str:
    t = (source or "").strip()
    if not t:
        return ""
    for cand in [Path(t), SB / t]:
        try:
            if cand.exists() and cand.is_file():
                return cand.read_text(encoding="utf-8")
        except OSError:
            pass
    return t


def digest_of(obj) -> str:
    s = json.dumps(obj, sort_keys=True)
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def elaborate(source: str):
    """Load JSON IR from path or raw string, type-check minimal §2 shape.

    Returns (ir_dict, program_digest). Raises ValueError with location on ill-typed.
    """
    text = _load_text(source)
    if not text:
        raise ValueError("empty program (location: program)")
    try:
        ir = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"ill-typed program: invalid JSON at {e.lineno}:{e.colno}") from e
    if not isinstance(ir, dict):
        raise ValueError("ill-typed program: top-level must be object (location: program)")
    for key in ("schemas", "models"):
        if key not in ir:
            raise ValueError(f"ill-typed program: missing '{key}' (location: program.{key})")
    for i, s in enumerate(ir.get("schemas", [])):
        for f in ("name", "sorts", "arrows"):
            if f not in s:
                raise ValueError(f"ill-typed schema[{i}]: missing '{f}' (location: schemas[{i}].{f})")
    for i, m in enumerate(ir.get("models", [])):
        if "name" not in m:
            raise ValueError(f"ill-typed model[{i}]: missing 'name' (location: models[{i}].name)")
    return ir, digest_of(ir)


def load_contracts():
    p = SB / "stage0_contracts.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(d, dict):
        return d.get("generators", [])
    return d
