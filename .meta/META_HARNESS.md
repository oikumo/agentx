#META_HARNESS

DEF:OMT++ enforcement (A→D→P→T). Gates src/ edits.

R1:src/edit→omt_phase{tt:bug_fix|minor|major|new|refactor|test|docs, ph:A|D|P|T, sc:"done"}

R2:major|new→design_*.md on disk. Scaffold:uv run scripts/omt/new_feature.py "<n>" --type major

R3:TDD auto for major/new in P.

TDD:TS=list behaviors; RD=tests/ only (fail); GN=src/ only (pass); RF=src/ only (green, auto-rev); DN=suite pass

RIGOR:tt∈{bug_fix,minor,refactor,test}→phase_only; tt∈{major,new}→phase+design; docs→none

COMP:ENF=.opencode/plugin/omt_enforcer.ts; STS=.opencode/plugin/omt_status.ts; LNT=scripts/omt/mvc_check.py; TDD=scripts/omt/tdd_check.py; SCAF=scripts/omt/new_feature.py; LG=.meta/.omt/ledger.jsonl; RUL=opencode.jsonc,AGENTS.md

ERR:block:V→M(ui/←model.*), M→UI(model/←ui.*), PRT≠ABC(no ABC+@abs)

WRN:toast:SQL∉DP(¬*_db.py has SQL), GC>300, CTL_UI(print() in ctl)

PROT:README.md,uv.lock,LICENSE,.env,tests/(omt_skip{sc:tests})

ESC:omt_skip{rsn:"", sc:src|tests|all}→logged

EXT:omt_complete{ft:"feature_XXX"}→verify, sync WORK.md[x]

STS:uv run scripts/omt/tdd_check.py status→ph, TDD_state, pend

PTH:M=.meta/software_development_process/omt_agent_guide.md; DS=.meta/software_development_process/4.design/features/feature_XXX/; TS=.meta/software_development_process/6.testing/features/feature_XXX/; WK=WORK.md; RL=AGENTS.md

TREE:src?→phase→major/new?→design→TDD?→RD→GN→RF→DN; tst?→canary|RD; doc?→no_phase

CMDS:omt_phase,omt_skip,omt_complete,omt_testlist,omt_red,omt_green,omt_refactor,omt_done,mvc_check.py,new_feature.py

GATE:mechanical, no manual discipline