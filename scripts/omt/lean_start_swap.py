#!/usr/bin/env python3
"""lean_start_swap — mh14 run001 STARTUP variant swap (feature_135, D3).

Reversible single-surface config-swap between the two run001 variants of the
session-start instruction:

  control        current SESSION STARTUP line of .agents_prompts/build.md
                 (byte-pinned below; = AGENTS.md STARTUP behavior as-is)
  lean_start_v1  same line + `LEAN_START_V1` marker + one appended clause:
                 render the menu directly as plain text in the same reply,
                 never call the `startup_table` tool (kills the F4
                 double-render: tool body + agent relay)

Design (PROJECT.md meta_harness_14):
- Surface = .agents_prompts/build.md ONLY. It rides the system prompt via
  opencode.jsonc `{file:./.agents_prompts/build.md}` — the surface that
  produced the measured 3-roundtrip start (read + probe + startup_table).
  .meta/META_HARNESS.omt / AGENTS.md stay byte-identical across variants:
  AGENTS.md "Show ..." is render-agnostic, and @budget agents_md 3511/3584
  has no headroom for a lean payload — swapping only build.md keeps the
  variant single-factor (D3 "restore after each trial" = swap back).
- Pinned constants: refusal (exit 2, no write) when the live line matches
  neither pinned variant — protects hand-edited states from being clobbered
  and keeps trials honest (control is exactly the recorded baseline).
- Trials are human-launched (mh13 D7): the user starts each opencode session
  with the run001 label as the first user message; this script only flips
  the config before/after each trial.

Usage:
  uv run scripts/omt/lean_start_swap.py --status            (default; safe)
  uv run scripts/omt/lean_start_swap.py --variant lean_start_v1
  uv run scripts/omt/lean_start_swap.py --variant control
"""
# TA: why: build.md-only swap — .agents_prompts/build.md is the {file:} include
# behind the agent system prompt (opencode.jsonc:12), NOT a harnessc projection;
# swapping it needs no `harnessc build`, cannot bust @budget agents_md (73B
# headroom), and leaves AGENTS.md/@doc startup byte-identical so the variant
# differs in exactly one factor (D19 attribution cleanliness).
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_MD = REPO_ROOT / ".agents_prompts" / "build.md"

LEAN_MARKER = "LEAN_START_V1"
ANTI_TOOL_CLAUSE = (
    "Render the menu directly as plain text in that same reply "
    "— do NOT call the `startup_table` tool (single render; F4 double-render diet)."
)

# Pinned control: byte-exact SESSION STARTUP line of .agents_prompts/build.md
# (drift-guarded by tests/features/feature_135.lean_start_v1_variant/).
CONTROL_LINE = (
    "Read `WORK.compiled.md` (11-line startup header; full detail in `WORK.md` on demand) "
    "+ 1x `omt_net` probe at session start with `max_states=0` "
    "(brief: observation+menu+freshness); render INTRO (1 paragraph: what this menu is "
    "+ where data comes from + reply single letter) + `GLOBAL` (<=8 lines: net "
    "observation/rev, Pool p/a/d, Lanes, Projects active/complete/draft, drift "
    "counts, STALE if `WORK.compiled.md` NEXT != probe next) + `TASKS` menu "
    "(grouped Projects/Drifts/New, active+not-started only; labels without "
    "`proj:`/`drift:`/`unscoped:` prefixes; NEXT/Other/Blocked/Resources order) as "
    "letter-shortcut list (A/B/C... mapped 1:1 to stable `Options:` IDs, no "
    "invented IDs in TASKS, D19; user replies with single letter, never "
    "question-tool) + `SUGGESTED NEXT` (advisory D19-exempt <=5 lines: "
    "drift-priority unlinked > aging > iter-log + pool state + <=2 IDEA: items, "
    "shortcut S = accept, never auto-applied). Rest on demand via `omt_nav` "
    "(op=nav|list_sections|cross_ref|quick_ref)."
)

# Lean variant is DERIVED from control (marker prefix + clause suffix) so the
# delta is structural, not transcribed — strip_variant() inverts it exactly.
LEAN_LINE = f"{LEAN_MARKER} — {CONTROL_LINE} {ANTI_TOOL_CLAUSE}"

# Enforcement tokens every variant must carry (zero gate regression, F-evidence
# contract: menu content, OptionID 1:1 map, STALE semantics, question-tool ban).
CONTROL_ENFORCEMENT_TOKENS = (
    "Read `WORK.compiled.md`",
    "11-line startup header",
    "`omt_net` probe",
    "`max_states=0`",
    "render INTRO",
    "`GLOBAL` (<=8 lines",
    "STALE if `WORK.compiled.md` NEXT != probe next",
    "`TASKS` menu",
    "mapped 1:1 to stable `Options:` IDs",
    "no invented IDs in TASKS, D19",
    "never question-tool",
    "`SUGGESTED NEXT`",
    "shortcut S = accept, never auto-applied",
    "Rest on demand via `omt_nav`",
)

VARIANTS = ("control", "lean_start_v1")

# run001 trial label template (mh13 protocol: first user-message line;
# full rendered label lines come from `omt_session` experiment dry_run).
LABEL_TEMPLATE = (
    '[mh13.experiment] {{"v":1,"experiment":"mh14_session_start_token_cost",'
    '"run":"run001","trial":"{case}_{variant}_rep{rep:02d}","case":"{case}",'
    '"variant":"{variant}","rep":{rep},"attempt":1,"event":"trial_start"}}'
)


def strip_variant(line: str) -> str:
    """Invert LEAN_LINE back to CONTROL_LINE (exact marker/clause removal)."""
    return line.removeprefix(f"{LEAN_MARKER} — ").removesuffix(f" {ANTI_TOOL_CLAUSE}")


def detect_variant(text: str) -> str | None:
    """'control' | 'lean_start_v1' | None when the live line matches neither.

    Compares exact FULL lines (text.split("\\n")): CONTROL_LINE is a substring
    of LEAN_LINE (marker prefix + clause suffix), so substring containment
    cannot disambiguate — line equality does.
    """
    lines = text.split("\n")
    if lines.count(CONTROL_LINE):
        return "control"
    if lines.count(LEAN_LINE):
        return "lean_start_v1"
    return None


def swap_variant(path: Path, variant: str) -> dict:
    """Swap the STARTUP line of `path` to `variant`.

    Idempotent when already at `variant`; refuses (SystemExit 2, no write)
    when the current line matches neither pinned variant.
    """
    if variant not in VARIANTS:
        raise SystemExit(f"unknown variant: {variant!r} (expected {VARIANTS})")
    text = path.read_text()
    current = detect_variant(text)
    if current == variant:
        return {"ok": True, "variant": variant, "changed": 0, "path": str(path)}
    if current is None:
        sys.stderr.write(
            f"refusing swap on {path}: STARTUP line matches neither pinned "
            "variant (control | lean_start_v1) — re-pin constants first "
            "(tests/features/feature_135.lean_start_v1_variant/ guards drift)\n"
        )
        raise SystemExit(2)

    src = CONTROL_LINE if current == "control" else LEAN_LINE
    dst = LEAN_LINE if variant == "lean_start_v1" else CONTROL_LINE
    lines = text.split("\n")
    assert lines.count(src) == 1, f"expected exactly one STARTUP line, got {lines.count(src)}"
    new_text = "\n".join(line if line != src else dst for line in lines)
    path.write_text(new_text)

    # verify: exactly one swapped full line, everything else untouched
    reread = path.read_text()
    reread_lines = reread.split("\n")
    ok = (reread_lines.count(dst) == 1
          and "\n".join(l if l != dst else src for l in reread_lines) == text)
    if not ok:
        # restore best-effort before failing loudly
        path.write_text(text)
        raise SystemExit("post-swap verification failed; original restored")
    return {"ok": True, "variant": variant, "changed": 1, "path": str(path)}


def _status_lines() -> list[str]:
    text = BUILD_MD.read_text()
    current = detect_variant(text)
    state = current or "UNKNOWN (matches neither pinned variant — refusing swaps)"
    lines = [
        "mh14 run001 STARTUP variant status",
        f"  surface : .agents_prompts/build.md (system-prompt {{file:}} include)",
        f"  variant : {state}",
        "  other   : .meta/META_HARNESS.omt + AGENTS.md untouched by this swap",
        f"  AGENTS.md @budget agents_md headroom: 3584-3511 = 73 B (kept)",
    ]
    if current == "lean_start_v1":
        lines.append("  next    : run trial(s), then RESTORE via --variant control")
    elif current == "control":
        lines.append(
            "  next    : --variant lean_start_v1 flips the config for a trial "
            "(restore with --variant control)"
        )
    return lines


def main(argv: list[str] | None = None) -> tuple[int, str]:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("--variant", "-v"):
        if len(argv) < 2:
            return 2, "usage: lean_start_swap.py [--variant control|lean_start_v1] | [--status]"
        report = swap_variant(BUILD_MD, argv[1])
        out_lines = [f"swapped -> {report['variant']} ({report['changed']} line(s))"]
        if report["variant"] == "lean_start_v1":
            out_lines += [
                "",
                "run001 reminder — the user starts each trial session with the",
                "label as the FIRST user-message line (mh13 protocol), e.g.:",
                LABEL_TEMPLATE.format(case="fresh_session_menu",
                                      variant="lean_start_v1", rep=1),
                "cases: fresh_session_menu | known_task_resume — reps 1..2 each,",
                "control AND lean (8 trials, run001).",
                "After the trial: restore with --variant control.",
            ]
        return 0, "\n".join(out_lines)
    # default: --status (safe, no writes)
    return 0, "\n".join(_status_lines())


if __name__ == "__main__":
    rc, out = main()
    print(out)
    sys.exit(rc)
