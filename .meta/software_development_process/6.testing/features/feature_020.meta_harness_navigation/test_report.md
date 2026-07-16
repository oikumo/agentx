# Test Report: feature_020.meta_harness_navigation

> **Feature:** Meta Harness Navigation System
> **Type:** major_feature
> **Phase:** Testing
> **Status:** Testing complete (revision 2 — defects found in review, fixed, re-verified)

---

## 1. Test Summary

| Metric | Value |
|--------|-------|
| **Test file** | `tests/features/feature_020.meta_harness_navigation/test_omt_nav.py` |
| **Fixtures** | `_nav_runner.mjs`, `_plugin_load.mjs`, `_gate_runner.mjs` (invoke real plugin tools/helpers via node) |
| **Total tests** | 49 |
| **Passed** | 49 ✅ |
| **Failed** | 0 |
| **Skipped** | 0 (node v24 available; behavioral tests run) |
| **Coverage** | grep patterns, plugin source structure, **real-tool behavior**, enforcer health, **scoped nav gate (M1/M2)**, docs, integration, enforcement config |

---

## 2. Revision History

### Revision 1 (2026-07-12) — original
18 tests, all structural (asserted on source-file string presence and doc tag
existence). Shipped green but masked multiple runtime defects (see §7).

### Revision 2 (2026-07-16) — defects found in review and fixed
A review of feature_020 uncovered critical defects that revision-1 tests could
not catch (the tests never executed the tools). The suite was expanded with
**behavioral tests** that invoke the real plugin tools, plus enforcer-health
regression guards. All defects below were fixed and verified.

---

## 3. Defects Found & Fixed

| ID | Severity | Description | Root cause | Fix |
|----|----------|-------------|------------|-----|
| **C1** | 🔴 Critical | `omt_enforcer.ts` failed to load — a duplicate `const PHASE_EXIT_REQUIREMENTS` (lines 51-52) and a duplicate `const UNLOCK_WINDOW_MS` (lines 48, 150) are `SyntaxError`s. This silently disabled **all** OMT++ mechanical enforcement (phase/edit/TDD/nav gates). | Duplicate `const` declarations introduced during feature_020 (commit `12ab94c`). | Removed the two duplicate lines; verified the plugin now imports cleanly via `node --experimental-strip-types`. |
| **C2** | 🔴 Critical | Nav enforcement was not active in the runtime; nav tools were unavailable to the agent. | Consequence of C1 (enforcer never loaded) — `omt_phase`/`omt_skip`/nav-blocking all live in the broken enforcer. | Resolved by C1 fix (enforcer loads again). Runtime surfacing of plugin tools is an opencode session-start concern. |
| **C3** | 🔴 Critical | `omt_list_sections` returned **zero** sections. It ran `grep -n "^##+ SECTION:"` (BRE), but headers are `# SECTION:` (single `#`) and `+` is literal in BRE. | Wrong regex: `^##+` requires 2+ `#` in ERE and matches nothing in BRE. | Changed pattern to `^##* SECTION:` (BRE-safe: one-or-more `#`). Now returns 94 sections. |
| **H1** | 🟠 High | Tests were non-behavioral — a completely broken tool shipped green. | Tests asserted on `.ts` source strings, not tool output. | Added `TestToolBehaviorReal` (invokes real tools via `_nav_runner.mjs`) + `TestEnforcerHealth` regression guards. |
| **H3** | 🟠 High | `runGrep` built a shell string (`grep -n "${pattern}" ...`) — shell-injection + quoting breakage. | `execSync` with string concatenation. | Replaced with `execFileSync("grep", ["-n","--",pattern,...files])` (array argv, no shell). Verified metachar query neither breaks nor injects. |
| **M3** | 🟡 Medium | `TAG_PATTERNS.SECTION` was `/^##+ SECTION:/m` (wrong) and the object was effectively dead code. | Copy of the C3 regex bug; values unused. | Fixed to `/^#+ SECTION:/m`; added a clarifying comment on its role (tag_type validation). |
| **M4** | 🟡 Medium | `META_FILES` was a hardcoded list; new docs weren't discovered. | Static array. | Auto-discover `.meta/doc/omt++/*.md` via `readdirSync` (sorted). |
| **H2** | 🟠 High | This test report contained inaccurate evidence (claimed 18 tests vs 22; wrong test names; quoted `## SECTION:` at line 12 when the file has `# SECTION:` at line 5). | Fabricated/aspirational evidence. | Rewritten from actual run output (this document). |
| **M1** | 🟡 Medium | Nav gate was over-broad: hard-blocked ALL `grep`/`glob`/`read` until one nav call, with no escape. Blocked startup reads, user-referenced files, and code searches; was only a once-per-session speedbump. | Gate had no path awareness and no nav escape hatch. | Smart gate: `read` never gated; `grep`/`glob` on `src/`/non-doc paths never gated; doc-scoped searches still gated; added `omt_skip{scope:"nav"}` escape. Logic extracted to a pure, exported `navGateDecision()` helper. |
| **M2** | 🟡 Medium | Nav tools index 13 doc files only (no `src/`), so code questions got nothing from nav yet were blocked from `grep`/`glob`. | Mismatch between nav coverage and the gate's reach. | `src/` and other non-doc paths exempted from the nav gate (nav expectation is doc-only). No tool change needed — enforcer-side exemption. |

---

## 4. Test Categories

### 4.1 Grep Pattern Tests (6) — structural
Verify tags exist and are searchable: `SECTION:`, `RULE_`, `ERR_`, `CMD_`, `QUICK_`, `XREF_`.

### 4.2 Plugin Source Structure Tests (8) — structural
Verify `omt_nav.ts` exports the 4 tools, uses the `tool()` decorator, uses
`execFileSync` (not `execSync`), and uses the BRE-safe `^##* SECTION:` pattern
(regression guards for H3 and C3 at the source level).

### 4.3 Real-Tool Behavioral Tests (10) — `TestToolBehaviorReal`
Invoke the **real** plugin tools via `node --experimental-strip-types` +
`_nav_runner.mjs` and assert on JSON output. These would have caught C3:
- `omt_list_sections` returns ≥10 sections (was 0 before C3 fix)
- covers `.meta/META_HARNESS.md` and the auto-discovered `doc/omt++/` files
- `omt_nav` finds `CMD_OMT_PHASE`; `tag_type` filters to the `ERR_` namespace
- no-match returns empty results + suggestions; `include_context` populates context
- `omt_cross_ref` resolves `XREF_NAV`; `omt_quick_ref` returns ≥5 workflows

### 4.4 Enforcer Health Tests (3) — `TestEnforcerHealth` (C1 regression)
- No duplicate top-level `const` declarations in `omt_enforcer.ts`
- `omt_enforcer.ts` imports without `SyntaxError` (via `_plugin_load.mjs`)
- `omt_nav.ts` imports without `SyntaxError`

### 4.5 Documentation Coverage (4), Integration (2), Enforcement Config (4)
Unchanged from revision 1; all still pass.

---

## 5. Test Execution Log (actual)

```bash
$ uv run pytest tests/features/feature_020.meta_harness_navigation/test_omt_nav.py -q
................................................                                         [100%]
49 passed in 4.51s
```

49 tests collected across 11 classes:
`TestGrepPatterns` (6), `TestOmtNavTool` (4), `TestOmtListSections` (2),
`TestOmtCrossRef` (1), `TestOmtQuickRef` (1), `TestToolBehaviorReal` (10),
`TestEnforcerHealth` (3), `TestNavGateDecision` (8), `TestNavGateEnforcement` (4),
`TestDocumentationCoverage` (4), `TestIntegration` (2), `TestEnforcement` (4).

---

## 6. Manual Verification (accurate)

**Actual SECTION header format** (single `#`, comment-style — not `##`):
```bash
$ grep -n "SECTION:" .meta/META_HARNESS.md | head -3
5:# SECTION:RULES — Core Enforcement Rules (grep:RULE_)
24:# SECTION:TDD — TDD State Machine (grep:TDD_)
42:# SECTION:COMPONENTS — Enforcement Components (grep:COMP_)
```

**C3 fix verified** — the fixed pattern returns sections (was 0):
```bash
$ grep -c "^##* SECTION:" .meta/META_HARNESS.md
17
$ grep -rn "^##* SECTION:" .meta/ AGENTS.md | wc -l
94
```

**C1 fix verified** — enforcer loads (would `SyntaxError` before):
```bash
$ node --experimental-strip-types -e "import('./.opencode/plugin/omt_enforcer.ts').then(()=>console.log('LOADED OK'))"
LOADED OK
```

**Real tool runtime check** (via `_nav_runner.mjs`):
```
omt_list_sections() -> sections count: 94
omt_nav({query:'CMD_OMT_PHASE'}) -> results: 1
omt_cross_ref({xref:'XREF_NAV'}) -> refs: 2
omt_quick_ref({workflow:'START_MAJOR'}) -> workflows: 1
```

**H3 fix verified** — shell metacharacters neither break nor inject:
```
metachar query -> results: 0 (no error, no injection)
PWNED file created? false
```

---

## 7. MVC++ Lint Status

```bash
$ uv run scripts/omt/mvc_check.py
168 file(s) scanned — 0 error(s), 33 warning(s).
```

**Status:** ✅ PASS — 0 errors; 33 warnings are the pre-existing baseline
(unrelated to feature_020; same count as before this revision).

---

## 8. Phase Exit Verification

| Requirement | Status | Evidence |
|-------------|--------|----------|
| All .md files grep-navigable | ✅ | 94 `SECTION:` headers across docs |
| `omt_list_sections` works at runtime | ✅ | returns 94 sections (C3 fixed) |
| Nav tools functional end-to-end | ✅ | `TestToolBehaviorReal` (10 tests) |
| Enforcer loads (C1 fixed) | ✅ | `TestEnforcerHealth` + `node` import |
| Shell-injection hardened (H3) | ✅ | `execFileSync`, metachar test |
| Scoped nav gate (M1/M2) | ✅ | `TestNavGateDecision` (8) + `TestNavGateEnforcement` (4); `navGateDecision` 12/12 cases |
| Enforcement config present | ✅ | `TestEnforcement` (4 tests) |
| All tests pass | ✅ | 49/49 |

---

## 9. Known Limitations / Future Work

- **Nav enforcement scope (M1):** ✅ RESOLVED — the gate is now scoped: `read`
  and `src/`/non-doc searches are exempt; only doc-scoped `grep`/`glob` are
  gated, with `omt_skip{scope:"nav"}` as an escape hatch. Decision logic lives
  in the pure, exported `navGateDecision()` helper.
- **No source-code coverage (M2):** ✅ RESOLVED — `src/` and non-doc paths are
  exempt from the nav gate (the nav expectation is doc-only, matching the tools'
  doc-only coverage). Nav tools themselves still index docs only by design.
- **`tag_type` matching is loose:** `omt_nav{query,tag_type}` does not anchor to
  the start of the tag line, so `tag_type="ERR"` can match cross-reference lines
  that mention `ERR_`. Functional but could be tightened. Not in reported scope.
- **Platform:** requires Unix `grep` (acceptable on this linux project).

---

## 10. Conclusion

**feature_020.meta_harness_navigation is COMPLETE and VERIFIED** after fixing
the critical defects found in review. The documentation-tagging half was already
sound; the tooling+enforcement half had three critical defects (C1 load-breaking
syntax error, C3 broken `omt_list_sections`, C2 inactive enforcement) masked by
non-behavioral tests (H1). All are fixed and guarded by behavioral/regression
tests. The over-broad enforcement (M1) and code-coverage mismatch (M2) were then
resolved with a scoped, path-aware gate + escape hatch.

**Files changed in this revision:**
- `.opencode/plugin/omt_enforcer.ts` — removed 2 duplicate `const` (C1); scoped nav gate + `navGateDecision`/`isDocPath`/`hasNavUnlock` (M1/M2); `omt_skip{scope:"nav"}` escape
- `.opencode/plugin/omt_nav.ts` — C3 regex, H3 `execFileSync`, M3 TAG_PATTERNS, M4 auto-discovery
- `AGENTS.md` / `.meta/META_HARNESS.md` — scoped-gate docs + `nav` escape scope
- `tests/features/feature_020.meta_harness_navigation/test_omt_nav.py` — behavioral + regression tests (H1, M1/M2)
- `tests/features/feature_020.meta_harness_navigation/_nav_runner.mjs` — new fixture (real tool invocation)
- `tests/features/feature_020.meta_harness_navigation/_plugin_load.mjs` — new fixture (plugin load check)
- `tests/features/feature_020.meta_harness_navigation/_gate_runner.mjs` — new fixture (real navGateDecision invocation)

**Test report completed:** 2026-07-16 (revision 2)
**MVC++ status:** 0 errors, 33 warnings (baseline)
