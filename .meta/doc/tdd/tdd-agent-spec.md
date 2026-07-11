# TDD_SPEC v5 :: kent_beck :: python+uv_only :: agent_exec

TOOLCHAIN: uv only. no pip/venv/poetry/conda. init=`uv init` add=`uv add --dev pkg` sync=`uv sync` run=`uv run pytest`

LAWS: L1 no-prod-code-without-failing-test | L2 test=min-to-fail(compile/import/collect-err counts) | L3 prod=min-to-pass-current-test-only. violation->revert-last-edit

## PHILOSOPHY (judgment source when rules underspecify a situation)
core_fear->confidence: tests replace anxiety w/ empirical proof of correctness. purpose=control fear, not eliminate all bugs
stride_variable: uncertain/scared/unfamiliar-code->shrink step size toward trivial(even 1-line); confident/familiar->take bigger steps. same laws apply at any stride length, only granularity changes
two_hats_never_same_time: "make it work" hat(RED/GREEN, behavior) XOR "make it right" hat(REFACTOR, structure). never wear both simultaneously->this is why L3(GREEN)+dedup(REFACTOR) are separate states, not merged
simple_design_priority(Beck's 4 rules, apply in strict order, higher rule always wins conflict):
  1.passes_all_tests(no design matters if behavior wrong)
  2.reveals_intent(names/structure communicate purpose to next reader)
  3.no_duplication(DRY: same knowledge expressed twice->extract)
  4.fewest_elements(no class/method/abstraction not currently earning its keep)
yagni: do not add generality/flexibility/abstraction a test has not yet demanded. speculative future-proofing violates L3+rule4. wait for 2nd concrete example(triangulate) before generalizing, never guess ahead
tests_as_design_tool_not_just_verification: writing test-first forces usable/intention-revealing API design before impl exists. if a test is awkward to write, that is a design-smell signal on the prod code, not just the test
design_emerges_incrementally: no big-upfront-design. architecture is grown via repeated REFACTOR passes responding to duplication actually observed, not anticipated
economics_of_steps: smaller steps = more frequent feedback = cheaper mistakes = lower cognitive load. if stuck/confused/many-things-broken->this is a signal step was too large, shrink it, don't push through
courage_enabled_by_safety_net: a green suite is what makes bold refactoring safe. never refactor without a passing suite as the safety net(see FAILURE_RECOVERY)

## FSM
TESTLIST(enumerate behaviors,no code)->RED(write 1 test fn;`uv run pytest -x -q f`;require exit!=0,reason∈{AssertionError,ModuleNotFoundError,AttributeError,ImportError};else fix test,retry)->GREEN(min prod code;`uv run pytest -x -q`;require exit==0)->REFACTOR(dedupe;`uv run pytest -q` after EACH micro-edit;fail->revert edit)->loop RED until test_list empty & no new items surfaced=DONE

## GREEN strategy select
first_test&rule_unclear->FAKE_IT(return literal const) | rule_obvious&low_risk->OBVIOUS(write real logic; >1 unrelated test breaks->abort,fallback FAKE_IT+TRIANGULATE) | else->TRIANGULATE(add 2nd example breaking current const->forces generalization; collapse to `@pytest.mark.parametrize` only in REFACTOR, never RED/GREEN)
```python
def total(xs): return 0                    # FAKE_IT
def add(a:int,b:int)->int: return a+b       # OBVIOUS
def test_a(): assert total([])==0           # green via fake
def test_b(): assert total([5])==5          # breaks fake->generalize:
def total(xs:list[int])->int: return sum(xs)
```

## test constraints
fn-scoped `@pytest.fixture`, no globals, order-independent | deterministic: inject time/random/io via `monkeypatch`/`unittest.mock.patch`, no live net/clock/unseeded-rand | 1 behavior/test | name=`test_<subject>_<behavior>` | plain `assert` not `unittest.TestCase`

## refactor triggers (apply only on GREEN, never mixed w/ RED/GREEN edits)
dup_setup->fixture | dup_shape_diff_vals->parametrize | magic_literal->const/Enum | mutable_shared_state->`@dataclass(frozen=True)` | repeated_pattern->functools/itertools/collections | missing_types->add hints,`uv run mypy f` | new_behavior_noticed->append test_list,DO NOT implement now

## anti-patterns->fix
prod-before-test->test first | test+impl same step unverified->run,observe fail first | full-solution-on-test#1->FAKE_IT first | batch-N-tests-batch-fix->1 test:1 min impl loop | refactor-while-red->fix green first | new-behavior-during-refactor->defer to test_list | skip-refactor-bc-green->always scan,"none found" valid | `skip`/`xfail`-to-force-green->forbidden | test-written-only-to-hit-coverage%->forbidden, test only for real uncovered behavior

## failure recovery
GREEN raises unexpected SyntaxError/TypeError -> discard edit, revert last-pass state, retry FAKE_IT
REFACTOR breaks suite -> `git checkout -- f` (or in-mem revert), restore last-GREEN state exactly, never patch-forward on red

## uv commands
`uv run pytest -x -q f` 1file-stop-on-fail | `uv run pytest -x -q f::test_name` 1fn | `uv run pytest -q` full | `uv run pytest -m "not slow"` skip-slow | `uv run pytest --cov=pkg --cov-report=term-missing` coverage | `uv run pytest --lf` rerun-failed | `uv run mypy pkg/` typecheck

## trace: money/dollar (canonical)
test_list=[5*2=10, immutability]
RED Dollar(5).times(2).amount==10 -> ModuleNotFoundError(valid)
GREEN money.py: `__init__` sets `self.amount=10`(FAKE),`times()` noop -> 1 passed
RED same fn+= Dollar(6).times(2).amount==12 -> AssertionError 10==12(TRIANGULATE)
GREEN `self.amount=amount; times(m): self.amount*=m` -> passed. note mutation smell->test_list+=immutability
RED new test: product=five.times(2); product.amount==10 AND five.amount==5(unmutated) -> fails(mutating impl can't satisfy)
GREEN `@dataclass(frozen=True) class Dollar: amount:int` + `times(m)->Dollar: return Dollar(self.amount*m)` -> passed
REFACTOR `uv run mypy money.py` clean
test_list empty->DONE
NOTE: contract change(mutating->immutable)=new RED/GREEN cycle NOT refactor. refactor never changes asserted behavior.

## done_checklist
[ ] every prod line traces to a test that demanded it
[ ] test_list empty, no new items last cycle
[ ] `uv run pytest -q`->0 failed/error, no new skip/xfail
[ ] no uncovered branch in files touched (`--cov`, check Missing col)
[ ] refactor recorded per GREEN cycle: applied-X | none-found
[ ] names=test_<subject>_<behavior>

## summary_token
RED(pytest -x -q,expect-fail)->GREEN(fake|obvious|triangulate,pytest -x -q,expect-pass)->REFACTOR(fixture/parametrize/const/frozen-dataclass,pytest -q per micro-edit)->loop test_list->empty. never skip refactor. never batch untested behavior. never mutate contract inside refactor. uv only.
