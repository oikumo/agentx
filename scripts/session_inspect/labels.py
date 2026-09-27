"""labels.py — [mh13.experiment] v1 parser/binder + legacy discharge adapter.

Label protocol v1 (PROJECT.md, design_001 §5): exact-prefix JSON label lines,
closed event set, trial identity established at trial_start and enforced
afterwards. Only role=user message parts mint trials; titles, tool outputs,
and assistant text are echoes (echo_not_trial). Legacy discharge labels
bind only under an explicit run mapping; absent rep/attempt stay unavailable.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from .normalize import normalize_snapshot
from .schema import Finding, SourceRef

LABEL_PREFIX = "[mh13.experiment]"

EVENTS: frozenset = frozenset({
    "trial_start", "trial_end", "span_start", "span_end", "checkpoint",
})

LEGACY_RE = re.compile(
    r"^\[harness_reason:discharge arm=(harness|planner|kernel) case=(H1|H3)\]$")

_TRIAL_START_REQUIRED = frozenset({"experiment", "case", "variant", "rep"})
_CORE_REQUIRED = frozenset({"v", "run", "trial", "attempt", "event"})

LEGACY_EXPERIMENT = "harness_reason_discharge"


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------
@dataclass
class TrialIdentity:
    protocol_version: Optional[int] = None
    experiment: Optional[str] = None
    run: Optional[str] = None
    trial: Optional[str] = None
    case: Optional[str] = None
    variant: Optional[str] = None
    rep: Optional[int] = None
    attempt: Optional[int] = None


@dataclass
class ParsedLabel:
    identity: TrialIdentity
    event: str
    fields: dict[str, Any] = field(default_factory=dict)
    raw: str = ""


@dataclass
class SpanRecord:
    id: str
    parent_span: Optional[str] = None
    started: bool = False
    closed: bool = False
    reversed: bool = False


@dataclass
class TrialRecord:
    identity: TrialIdentity
    has_start: bool = False
    complete: bool = False
    outcome: Optional[str] = None
    session_ids: list[str] = field(default_factory=list)
    spans: dict[str, SpanRecord] = field(default_factory=dict)
    checkpoints: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LabelBinding:
    trials: dict[str, TrialRecord] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    echoes: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# v1 grammar
# ---------------------------------------------------------------------------
def _grammar_invalid(raw: str, reason: str,
                     ref: Optional[SourceRef] = None) -> Finding:
    return Finding("label_grammar_invalid", {"raw": raw, "reason": reason}, ref)


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def parse_label_line(line: str,
                     ref: Optional[SourceRef] = None) -> ParsedLabel | Finding:
    """Parse one message-text line. Failures return a Finding preserving raw."""
    if not isinstance(line, str) or not line.startswith(LABEL_PREFIX):
        return _grammar_invalid(line if isinstance(line, str) else "",
                                "missing_exact_prefix", ref)
    rest = line[len(LABEL_PREFIX):].strip()
    if not rest.startswith("{"):
        return _grammar_invalid(line, "no_json_object", ref)
    try:
        obj = json.loads(rest)
    except (json.JSONDecodeError, ValueError):
        return _grammar_invalid(line, "invalid_json", ref)
    if not isinstance(obj, dict):
        return _grammar_invalid(line, "object_not_mapping", ref)

    event = obj.get("event")
    if event not in EVENTS:
        return _grammar_invalid(line, f"unknown_event:{event!r}", ref)
    if not all(k in obj for k in _CORE_REQUIRED):
        missing = sorted(k for k in _CORE_REQUIRED if k not in obj)
        return _grammar_invalid(line, f"missing_core:{missing}", ref)
    if obj.get("v") != 1 or not _is_int(obj.get("v")):
        return _grammar_invalid(line, "protocol_version_not_1", ref)
    for int_field in ("rep", "attempt"):
        if int_field in obj and obj[int_field] is not None \
                and not _is_int(obj[int_field]):
            return _grammar_invalid(line, f"{int_field}_not_int", ref)
    for str_field in ("experiment", "run", "trial", "case", "variant"):
        if str_field in obj and obj[str_field] is not None \
                and not isinstance(obj[str_field], str):
            return _grammar_invalid(line, f"{str_field}_not_str", ref)
    if event == "trial_start":
        missing = sorted(k for k in _TRIAL_START_REQUIRED if k not in obj)
        if missing:
            return _grammar_invalid(
                line, f"trial_start_incomplete:{missing}", ref)
    if event in ("span_start", "span_end") and "span" not in obj:
        return _grammar_invalid(line, f"{event}_missing_span", ref)
    if event == "checkpoint" and "checkpoint_id" not in obj:
        return _grammar_invalid(line, "checkpoint_missing_id", ref)

    identity = TrialIdentity(
        protocol_version=obj.get("v"), experiment=obj.get("experiment"),
        run=obj.get("run"), trial=obj.get("trial"), case=obj.get("case"),
        variant=obj.get("variant"), rep=obj.get("rep"),
        attempt=obj.get("attempt"))
    reserved = _CORE_REQUIRED | {"experiment", "case", "variant", "rep",
                                 "outcome", "span", "parent_span",
                                 "checkpoint_id"}
    return ParsedLabel(identity=identity, event=event,
                       fields={k: v for k, v in obj.items() if k not in reserved
                               or k in ("outcome", "span", "parent_span",
                                        "checkpoint_id")},
                       raw=line)


# ---------------------------------------------------------------------------
# Legacy adapter (feature_130 labels)
# ---------------------------------------------------------------------------
def parse_legacy_discharge(line: str, *,
                           run_mapping: Optional[dict[str, Any]] = None,
                           ref: Optional[SourceRef] = None) -> ParsedLabel | Finding:
    """Parse a legacy `[harness_reason:discharge arm=.. case=..]` line.

    Requires an explicit run mapping; absent rep/attempt/span boundaries stay
    unavailable (None) — repetitions are never invented.
    """
    text = line.strip() if isinstance(line, str) else ""
    match = LEGACY_RE.match(text)
    if not match:
        return Finding("label_grammar_invalid",
                       {"raw": line, "reason": "legacy_grammar_miss"}, ref)
    if not run_mapping or "run_id" not in run_mapping:
        return Finding("label_unbound_to_manifest",
                       {"raw": line, "reason": "run_mapping_required"}, ref)
    arm, case = match.group(1), match.group(2)
    identity = TrialIdentity(
        protocol_version=None,
        experiment=run_mapping.get("experiment", LEGACY_EXPERIMENT),
        run=run_mapping["run_id"], trial=f"{arm}:{case}", case=case,
        variant=arm, rep=None, attempt=None)
    return ParsedLabel(identity=identity, event="legacy_label",
                       fields={"arm": arm, "case": case}, raw=line)


# ---------------------------------------------------------------------------
# Binder
# ---------------------------------------------------------------------------
def _agrees(trial: TrialRecord, parsed: ParsedLabel) -> bool:
    """Later events must agree with the identity trial_start established."""
    ident = trial.identity
    for attr in ("experiment", "case", "variant", "rep"):
        new = getattr(parsed.identity, attr)
        if new is not None and getattr(ident, attr) != new:
            return False
    return True


def _trial_key(parsed: ParsedLabel) -> tuple:
    return (parsed.identity.run, parsed.identity.trial,
            parsed.identity.attempt)


def bind_labels(snapshot: dict[str, Any], *, manifest: Any = None,
                run_mapping: Optional[dict[str, Any]] = None) -> LabelBinding:
    """Bind label lines in user message text to trials.

    Accepts a raw adapter snapshot or already-normalized records. Only
    role=user text/tool parts mint trials; everything else is an echo.
    trial_start establishes identity; later events must agree with it.
    """
    records = snapshot
    if (isinstance(snapshot.get("messages"), list) and snapshot["messages"]
            and isinstance(snapshot["messages"][0], dict)):
        records = normalize_snapshot(snapshot)
    schema_markers = ((snapshot.get("coverage") or {}).get("schema_markers")
                      if isinstance(snapshot.get("coverage"), dict) else {}) or {}
    ref = SourceRef(path="labels", schema_markers=schema_markers)

    binding = LabelBinding()
    roles = {m.id: m.role for m in records.get("messages", ())}
    ordered = sorted(records.get("parts", ()),
                     key=lambda p: (p.time.get("created") or 0, p.id))

    pending_ends: dict[tuple, list[tuple[str, int]]] = {}
    pos = 0

    def note_echo(p: Any, raw: str, context: str) -> None:
        binding.echoes.append({"session_id": p.session_id,
                               "message_id": p.message_id,
                               "part_id": p.id, "line": raw,
                               "context": context})
        binding.findings.append(Finding(
            "echo_not_trial",
            {"session_id": p.session_id, "message_id": p.message_id,
             "part_id": p.id, "context": context},
            ref))

    for part in ordered:
        role = roles.get(part.message_id)
        candidates: list[tuple[str, str]] = []  # (line, context)
        if part.type == "text" and isinstance(part.payload.get("text"), str):
            for ln in part.payload["text"].splitlines():
                if ln.startswith(LABEL_PREFIX):
                    candidates.append((ln, "user_text" if role == "user"
                                       else "assistant_text"))
                elif role == "user" and LEGACY_RE.match(ln.strip()) \
                        and run_mapping is not None:
                    parsed_legacy = parse_legacy_discharge(
                        ln, run_mapping=run_mapping, ref=ref)
                    if isinstance(parsed_legacy, Finding):
                        binding.findings.append(parsed_legacy)
                    else:
                        _ingest_legacy(binding, parsed_legacy, part)
        elif part.type == "tool":
            state = part.payload.get("state") or {}
            output = state.get("output") or (part.payload.get("metadata") or {}).get("output")
            if isinstance(output, str):
                for ln in output.splitlines():
                    if ln.startswith(LABEL_PREFIX):
                        candidates.append((ln, "tool_output"))
        for raw, context in candidates:
            parsed = parse_label_line(raw, ref)
            if isinstance(parsed, Finding):
                binding.findings.append(parsed)
                continue
            if role != "user":
                note_echo(part, raw, context)
                continue
            pos += 1
            _ingest_event(binding, parsed, part, pos, ref, pending_ends)

    # pending ends with no matching start -> orphan
    for key, ends in pending_ends.items():
        for span_id, _ in ends:
            if key[1] not in binding.trials or \
                    span_id not in binding.trials[key[1]].spans:
                binding.findings.append(Finding(
                    "label_orphan_event",
                    {"run": key[0], "trial": key[1], "attempt": key[2],
                     "span": span_id}, ref))
    return binding


def _bind_session(trial: TrialRecord, part: Any) -> None:
    if part.session_id not in trial.session_ids:
        trial.session_ids.append(part.session_id)


def _ingest_legacy(binding: LabelBinding, parsed: ParsedLabel, part: Any) -> None:
    trial_id = parsed.identity.trial or ""
    trial = binding.trials.get(trial_id)
    if trial is None:
        trial = TrialRecord(identity=parsed.identity, has_start=True)
        binding.trials[trial_id] = trial
    _bind_session(trial, part)


def _ingest_event(binding: LabelBinding, parsed: ParsedLabel, part: Any,
                  pos: int, ref: SourceRef,
                  pending_ends: dict[tuple, list[tuple[str, int]]]) -> None:
    key = _trial_key(parsed)
    trial = binding.trials.get(key[1])

    if parsed.event == "trial_start":
        if trial is None:
            trial = TrialRecord(identity=parsed.identity, has_start=True)
            binding.trials[key[1]] = trial
            _bind_session(trial, part)
            return
        if trial.identity == parsed.identity:
            return  # idempotent identical repeat: dedupe, not an error
        binding.findings.append(Finding(
            "label_identity_conflict",
            {"run": key[0], "trial": key[1], "attempt": key[2],
             "reason": "trial_start_payload_differs"}, ref))
        return

    # non-start events require an established trial_start
    if trial is None or not trial.has_start:
        binding.findings.append(Finding(
            "label_orphan_event",
            {"run": key[0], "trial": key[1], "attempt": key[2],
             "event": parsed.event,
             "reason": "no_established_trial_start"}, ref))
        return
    if not _agrees(trial, parsed):
        binding.findings.append(Finding(
            "label_identity_conflict",
            {"run": key[0], "trial": key[1], "attempt": key[2],
             "event": parsed.event,
             "reason": "event_identity_disagrees"}, ref))
        return
    _bind_session(trial, part)

    if parsed.event == "trial_end":
        trial.complete = True
        trial.outcome = parsed.fields.get("outcome")
    elif parsed.event == "span_start":
        span_id = parsed.fields.get("span")
        if span_id in trial.spans:
            binding.findings.append(Finding(
                "label_identity_conflict",
                {"run": key[0], "trial": key[1], "span": span_id,
                 "reason": "duplicate_span_id"}, ref))
            return
        trial.spans[span_id] = SpanRecord(
            id=span_id, parent_span=parsed.fields.get("parent_span"),
            started=True)
        pend = pending_ends.get(key, [])
        earlier = [p for p in pend if p[0] == span_id]
        if earlier:
            # end observed before its start -> reversed interval
            trial.spans[span_id].reversed = True
            binding.findings.append(Finding(
                "span_reversed",
                {"run": key[0], "trial": key[1], "span": span_id}, ref))
            pending_ends[key] = [p for p in pend if p[0] != span_id]
    elif parsed.event == "span_end":
        span_id = parsed.fields.get("span")
        span = trial.spans.get(span_id)
        if span is not None and span.started and not span.closed \
                and not span.reversed:
            span.closed = True
        else:
            pending_ends.setdefault(key, []).append((span_id, pos))
    elif parsed.event == "checkpoint":
        trial.checkpoints.append(
            {"id": parsed.fields.get("checkpoint_id"), "fields": dict(parsed.fields)})
