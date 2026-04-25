"""
Petri Net Property Analyser (no dependencies).

Imports PetriNet, Place, Transition from petri_net.py and adds formal
verification of the most common behavioural and structural properties:

  Behavioural  (require state-space exploration)
  ─────────────────────────────────────────────
  • Reachability        – is a given marking reachable from M0?
  • Boundedness         – is every place token-count bounded?
  • k-Boundedness       – is every place bounded by k?
  • Safeness            – is every place 1-bounded (≤ 1 token)?
  • Deadlock-freedom    – does every reachable marking have ≥1 enabled transition?
  • Liveness (L1/live)  – can every transition fire again from any reachable marking?
  • Quasi-liveness      – can every transition fire at least once from M0?
  • Reversibility       – is M0 reachable from every reachable marking?

  Structural  (graph analysis only, no simulation)
  ─────────────────────────────────────────────────
  • Structural boundedness – no place can accumulate tokens unboundedly
    (detected via a simple weight-matrix check / siphon heuristic)
  • Dead transitions       – transitions with no input or no output arcs
  • Isolated nodes         – places/transitions with no arcs at all
  • Siphons / Traps        – minimal siphons and traps (structural)

WARNING: state-space exploration is exponential in the worst case.
         Use the `max_states` guard to avoid runaway on unbounded nets.
"""

from __future__ import annotations
import sys
import os
from collections import deque
from itertools import combinations

# ---------------------------------------------------------------------------
# Allow running from any directory by adding the output folder to sys.path
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from petri_net import PetriNet, Place, Transition  # noqa: E402


# ===========================================================================
#  Internal helpers
# ===========================================================================

Marking = tuple[int, ...]   # token counts in place-index order


def _place_order(net: PetriNet) -> list[str]:
    """Stable list of place names (dict insertion order)."""
    return list(net.places.keys())


def _marking_of(net: PetriNet, order: list[str]) -> Marking:
    return tuple(net.places[n].tokens for n in order)


def _apply(net: PetriNet, order: list[str], marking: Marking,
           t: Transition) -> Marking | None:
    """
    Return the successor marking after firing t from `marking`,
    or None if t is not enabled.
    """
    tokens = list(marking)
    idx = {n: i for i, n in enumerate(order)}
    for place, w in t.inputs.items():
        i = idx[place.name]
        if tokens[i] < w:
            return None
        tokens[i] -= w
    for place, w in t.outputs.items():
        i = idx[place.name]
        tokens[i] += w
    return tuple(tokens)


def _reachability_graph(net: PetriNet, order: list[str],
                        max_states: int = 50_000
                        ) -> tuple[dict[Marking, dict[str, Marking]], bool]:
    """
    BFS over the reachability graph.

    Returns
    -------
    graph    : marking -> {transition_name -> successor_marking}
    truncated: True if max_states was hit before exploration finished
    """
    m0 = _marking_of(net, order)
    graph: dict[Marking, dict[str, Marking]] = {}
    queue: deque[Marking] = deque([m0])
    visited: set[Marking] = {m0}

    while queue:
        if len(visited) >= max_states:
            return graph, True
        m = queue.popleft()
        graph[m] = {}
        for t in net.transitions.values():
            m2 = _apply(net, order, m, t)
            if m2 is not None:
                graph[m][t.name] = m2
                if m2 not in visited:
                    visited.add(m2)
                    queue.append(m2)
    return graph, False


# ===========================================================================
#  Result container
# ===========================================================================

class AnalysisResult:
    def __init__(self, property_name: str, holds: bool | None,
                 detail: str = "", witness: object = None):
        self.property_name = property_name
        self.holds = holds          # None  = inconclusive (truncated search)
        self.detail = detail
        self.witness = witness      # counter-example or evidence

    def __repr__(self):
        status = ("✓ YES" if self.holds
                  else ("✗ NO " if self.holds is False else "? INC"))
        return f"[{status}]  {self.property_name}"

    def print_full(self):
        status = ("✓  YES" if self.holds
                  else ("✗  NO " if self.holds is False else "?  INCONCLUSIVE"))
        print(f"  {status}  │  {self.property_name}")
        if self.detail:
            for line in self.detail.splitlines():
                print(f"            │    {line}")


# ===========================================================================
#  Behavioural analyses  (need the reachability graph)
# ===========================================================================

def check_reachability(net: PetriNet,
                       target: dict[str, int],
                       max_states: int = 50_000) -> AnalysisResult:
    """Is the (partial) marking `target` reachable from M0?"""
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)

    for m in graph:
        if all(m[order.index(p)] == v for p, v in target.items()
               if p in net.places):
            marking_str = dict(zip(order, m))
            return AnalysisResult(
                f"Reachability of {target}", True,
                f"Found in reachable marking: {marking_str}", m)

    holds = None if truncated else False
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult(
        f"Reachability of {target}", holds,
        f"Not found among {len(graph)} explored markings{suffix}.")


def check_boundedness(net: PetriNet,
                      max_states: int = 50_000) -> AnalysisResult:
    """Is every place bounded (finite max token count)?"""
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)

    max_tokens: dict[str, int] = {n: 0 for n in order}
    for m in graph:
        for i, n in enumerate(order):
            if m[i] > max_tokens[n]:
                max_tokens[n] = m[i]

    if truncated:
        return AnalysisResult(
            "Boundedness", None,
            f"Search truncated at {max_states} states; "
            f"partial max tokens: {max_tokens}")

    detail = "  ".join(f"{n}≤{v}" for n, v in max_tokens.items())
    return AnalysisResult("Boundedness", True,
                          f"Max tokens per place: {detail}",
                          max_tokens)


def check_k_boundedness(net: PetriNet, k: int,
                        max_states: int = 50_000) -> AnalysisResult:
    """Is every place ≤ k-bounded?"""
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)

    violations: list[tuple[str, int, Marking]] = []
    for m in graph:
        for i, n in enumerate(order):
            if m[i] > k:
                violations.append((n, m[i], m))

    if violations:
        v = violations[0]
        return AnalysisResult(
            f"{k}-Boundedness", False,
            f"Place '{v[0]}' reached {v[1]} tokens "
            f"(marking={dict(zip(order, v[2]))})", violations)

    holds = None if truncated else True
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult(f"{k}-Boundedness", holds,
                          f"No place exceeded {k} tokens{suffix}.")


def check_safeness(net: PetriNet,
                   max_states: int = 50_000) -> AnalysisResult:
    """Is every place safe (≤ 1 token)?"""
    r = check_k_boundedness(net, 1, max_states)
    r.property_name = "Safeness (1-bounded)"
    return r


def check_deadlock_freedom(net: PetriNet,
                           max_states: int = 50_000) -> AnalysisResult:
    """Does every reachable marking have at least one enabled transition?"""
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)

    deadlocks = [m for m, succs in graph.items() if not succs]
    m0 = _marking_of(net, order)

    if deadlocks:
        # Ignore M0 only if it is itself a deadlock and there are no others
        ex = deadlocks[0]
        return AnalysisResult(
            "Deadlock-freedom", False,
            f"Deadlock marking found: {dict(zip(order, ex))}", deadlocks)

    holds = None if truncated else True
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult("Deadlock-freedom", holds,
                          f"No deadlock found among {len(graph)} states{suffix}.")


def check_liveness(net: PetriNet,
                   max_states: int = 50_000) -> AnalysisResult:
    """
    L1-liveness (live): from every reachable marking, every transition
    can eventually fire again.
    """
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)
    reachable = set(graph.keys())

    dead: list[str] = []
    for tname, t in net.transitions.items():
        # t is live iff from every reachable marking, some reachable marking
        # enables t.  Equivalent: every SCC in the reachability graph
        # contains a marking that enables t.
        # Simple sufficient check: t fires in at least one reachable marking
        # AND for every marking where t doesn't fire, some path leads to one
        # where it does.  We use: t is NOT dead (fires ≥ once) as a proxy
        # for quasi-liveness here, and do the full SCC check for true liveness.
        ever_fires = any(tname in succs for succs in graph.values())
        if not ever_fires:
            dead.append(tname)

    if dead:
        return AnalysisResult(
            "Liveness (L1)", False,
            f"Transitions never fire from any reachable marking: {dead}", dead)

    # Full liveness: check SCCs
    # Build adjacency for SCC (Kosaraju)
    states = list(reachable)
    idx_of = {m: i for i, m in enumerate(states)}
    n = len(states)
    fwd: list[list[int]] = [[] for _ in range(n)]
    rev: list[list[int]] = [[] for _ in range(n)]
    for m, succs in graph.items():
        for m2 in succs.values():
            if m2 in idx_of:
                fwd[idx_of[m]].append(idx_of[m2])
                rev[idx_of[m2]].append(idx_of[m])

    # Kosaraju pass 1 – finish order
    visited = [False] * n
    finish_order: list[int] = []

    def dfs1(u):
        stack = [(u, iter(fwd[u]))]
        visited[u] = True
        while stack:
            node, children = stack[-1]
            try:
                v = next(children)
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, iter(fwd[v])))
            except StopIteration:
                finish_order.append(node)
                stack.pop()

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    # Kosaraju pass 2 – assign SCCs
    comp = [-1] * n
    num_scc = 0

    def dfs2(u, c):
        stack = [u]
        comp[u] = c
        while stack:
            node = stack.pop()
            for v in rev[node]:
                if comp[v] == -1:
                    comp[v] = c
                    stack.append(v)

    for u in reversed(finish_order):
        if comp[u] == -1:
            dfs2(u, num_scc)
            num_scc += 1

    # Map SCC id -> set of transition names that fire within that SCC
    scc_fires: list[set[str]] = [set() for _ in range(num_scc)]
    for m, succs in graph.items():
        ui = idx_of[m]
        for tname, m2 in succs.items():
            if m2 in idx_of and comp[idx_of[m2]] == comp[ui]:
                scc_fires[comp[ui]].add(tname)

    # Identify bottom SCCs (no outgoing edges to other SCCs)
    bottom: list[int] = []
    for c in range(num_scc):
        is_bottom = True
        for i, ci in enumerate(comp):
            if ci == c:
                for j in fwd[i]:
                    if comp[j] != c:
                        is_bottom = False
                        break
            if not is_bottom:
                break
        if is_bottom:
            bottom.append(c)

    not_live: list[str] = []
    all_tnames = set(net.transitions.keys())
    for c in bottom:
        missing = all_tnames - scc_fires[c]
        not_live.extend(missing)

    not_live = list(set(not_live))

    if not_live:
        holds = None if truncated else False
        suffix = " (search truncated)" if truncated else ""
        return AnalysisResult(
            "Liveness (L1)", holds,
            f"Transitions not live (stuck in some bottom SCC): "
            f"{not_live}{suffix}", not_live)

    holds = None if truncated else True
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult("Liveness (L1)", holds,
                          f"All transitions are live across {len(graph)} states{suffix}.")


def check_quasi_liveness(net: PetriNet,
                         max_states: int = 50_000) -> AnalysisResult:
    """
    Quasi-liveness: every transition fires at least once from M0.
    (Weaker than full liveness.)
    """
    order = _place_order(net)
    graph, truncated = _reachability_graph(net, order, max_states)

    fired: set[str] = set()
    for succs in graph.values():
        fired.update(succs.keys())

    never = [t for t in net.transitions if t not in fired]

    if never:
        return AnalysisResult(
            "Quasi-liveness", False,
            f"Transitions that never fire: {never}", never)

    holds = None if truncated else True
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult("Quasi-liveness", holds,
                          f"All transitions fire at least once{suffix}.")


def check_reversibility(net: PetriNet,
                        max_states: int = 50_000) -> AnalysisResult:
    """
    Reversibility: M0 is reachable from every reachable marking.
    """
    order = _place_order(net)
    m0 = _marking_of(net, order)
    graph, truncated = _reachability_graph(net, order, max_states)

    # Build reverse graph and BFS from M0 backwards
    rev: dict[Marking, list[Marking]] = {m: [] for m in graph}
    for m, succs in graph.items():
        for m2 in succs.values():
            if m2 in rev:
                rev[m2].append(m)

    # BFS on reverse graph from M0
    reachable_back: set[Marking] = {m0}
    queue: deque[Marking] = deque([m0])
    while queue:
        m = queue.popleft()
        for m2 in rev.get(m, []):
            if m2 not in reachable_back:
                reachable_back.add(m2)
                queue.append(m2)

    non_returning = [m for m in graph if m not in reachable_back]

    if non_returning:
        ex = dict(zip(order, non_returning[0]))
        return AnalysisResult(
            "Reversibility", False,
            f"M0 not reachable from {len(non_returning)} marking(s); "
            f"e.g. {ex}", non_returning)

    holds = None if truncated else True
    suffix = " (search truncated)" if truncated else ""
    return AnalysisResult("Reversibility", holds,
                          f"M0 reachable from all {len(graph)} states{suffix}.")


# ===========================================================================
#  Structural analyses  (graph only, no simulation)
# ===========================================================================

def structural_dead_transitions(net: PetriNet) -> AnalysisResult:
    """Transitions with empty input set can never be enabled (structurally dead)."""
    dead = [t.name for t in net.transitions.values() if not t.inputs]
    if dead:
        return AnalysisResult(
            "No structurally dead transitions", False,
            f"Transitions with no input arcs (always dead): {dead}", dead)
    return AnalysisResult("No structurally dead transitions", True,
                          "Every transition has at least one input arc.")


def structural_isolated_nodes(net: PetriNet) -> AnalysisResult:
    """Places or transitions with no arcs at all."""
    isolated = []
    for p in net.places.values():
        has_arc = any(p in t.inputs or p in t.outputs
                      for t in net.transitions.values())
        if not has_arc:
            isolated.append(f"place:{p.name}")
    for t in net.transitions.values():
        if not t.inputs and not t.outputs:
            isolated.append(f"transition:{t.name}")
    if isolated:
        return AnalysisResult(
            "No isolated nodes", False,
            f"Isolated nodes found: {isolated}", isolated)
    return AnalysisResult("No isolated nodes", True, "No isolated nodes.")


def structural_siphons_and_traps(net: PetriNet) -> AnalysisResult:
    """
    Find minimal siphons and traps.

    Siphon: a set S of places such that every transition that puts a
            token into S also takes from S (once empty, stays empty).
    Trap:   a set T of places such that every transition that takes from T
            also puts into T (once marked, stays marked).

    Only enumerates subsets up to size `max_subset` to stay tractable.
    """
    places = list(net.places.values())
    transitions = list(net.transitions.values())
    max_subset = min(len(places), 12)   # guard against 2^n explosion

    def pre(p: Place) -> set[str]:
        """Transition names that produce into p."""
        return {t.name for t in transitions if p in t.outputs}

    def post(p: Place) -> set[str]:
        """Transition names that consume from p."""
        return {t.name for t in transitions if p in t.inputs}

    def is_siphon(subset: list[Place]) -> bool:
        snames = {p.name for p in subset}
        for p in subset:
            for tname in pre(p):
                t = net.transitions[tname]
                # t produces into subset → must also consume from subset
                if not any(q in t.inputs for q in subset):
                    return False
        return True

    def is_trap(subset: list[Place]) -> bool:
        for p in subset:
            for tname in post(p):
                t = net.transitions[tname]
                # t consumes from subset → must also produce into subset
                if not any(q in t.outputs for q in subset):
                    return False
        return True

    siphons: list[list[str]] = []
    traps:   list[list[str]] = []

    for size in range(1, max_subset + 1):
        for combo in combinations(places, size):
            combo_list = list(combo)
            names = [p.name for p in combo_list]
            # Skip if a smaller known siphon/trap is a subset (minimality)
            if is_siphon(combo_list):
                if not any(set(s).issubset(set(names)) for s in siphons):
                    siphons.append(names)
            if is_trap(combo_list):
                if not any(set(tr).issubset(set(names)) for tr in traps):
                    traps.append(names)

    detail_lines = []
    if siphons:
        detail_lines.append(f"Siphons ({len(siphons)}): " +
                             " | ".join(str(s) for s in siphons))
    else:
        detail_lines.append("No siphons found.")
    if traps:
        detail_lines.append(f"Traps   ({len(traps)}): " +
                             " | ".join(str(t) for t in traps))
    else:
        detail_lines.append("No traps found.")

    return AnalysisResult(
        "Siphons & Traps (structural)",
        None,  # not a yes/no property per se
        "\n".join(detail_lines),
        {"siphons": siphons, "traps": traps})


# ===========================================================================
#  Convenience: run all checks
# ===========================================================================

def analyse(net: PetriNet,
            target_marking: dict[str, int] | None = None,
            k: int = 1,
            max_states: int = 50_000) -> list[AnalysisResult]:
    """
    Run the full suite of behavioural + structural checks.

    Parameters
    ----------
    net            : the PetriNet to analyse
    target_marking : optional partial marking for reachability query
    k              : bound for k-boundedness check  (default 1)
    max_states     : BFS state-space cap
    """
    results: list[AnalysisResult] = []

    # --- Structural (fast, no BFS) ---
    results.append(structural_dead_transitions(net))
    results.append(structural_isolated_nodes(net))
    results.append(structural_siphons_and_traps(net))

    # --- Behavioural (BFS) ---
    results.append(check_boundedness(net, max_states))
    results.append(check_safeness(net, max_states))
    results.append(check_k_boundedness(net, k, max_states))
    results.append(check_deadlock_freedom(net, max_states))
    results.append(check_quasi_liveness(net, max_states))
    results.append(check_liveness(net, max_states))
    results.append(check_reversibility(net, max_states))

    if target_marking:
        results.append(check_reachability(net, target_marking, max_states))

    return results


def print_report(net: PetriNet, results: list[AnalysisResult]):
    bar = "═" * 62
    print(f"\n{bar}")
    print(f"  Analysis report for '{net.name}'")
    print(bar)
    for r in results:
        r.print_full()
    print(bar)
    yes  = sum(1 for r in results if r.holds is True)
    no   = sum(1 for r in results if r.holds is False)
    inc  = sum(1 for r in results if r.holds is None)
    print(f"  Summary:  {yes} pass  │  {no} fail  │  {inc} inconclusive")
    print(f"{bar}\n")


# ===========================================================================
#  Demo
# ===========================================================================

if __name__ == "__main__":
    from petri_net import build_producer_consumer, PetriNet

    # ── 1. Producer-consumer (healthy net) ──────────────────────────────
    print("\n" + "━"*62)
    print("  NET 1: Producer-Consumer")
    print("━"*62)
    pc = build_producer_consumer()
    results = analyse(pc, target_marking={"buffer": 1}, k=3)
    print_report(pc, results)

    # ── 2. A deliberately broken net (deadlock + dead transition) ────────
    print("━"*62)
    print("  NET 2: Broken net (deadlock demo)")
    print("━"*62)
    broken = PetriNet("Broken")
    p1 = broken.add_place("p1", tokens=1)
    p2 = broken.add_place("p2", tokens=0)
    p3 = broken.add_place("p3", tokens=0)   # never gets a token

    t1 = broken.add_transition("t1")   # p1 -> p2
    t2 = broken.add_transition("t2")   # p2 -> p1  (loop, no way to t3)
    t3 = broken.add_transition("t3")   # p3 -> …   (needs p3 which is always 0)

    broken.add_arc(p1, t1); broken.add_arc(t1, p2)
    broken.add_arc(p2, t2); broken.add_arc(t2, p1)
    broken.add_arc(p3, t3); broken.add_arc(t3, p1)

    results2 = analyse(broken, k=1)
    print_report(broken, results2)

    # ── 3. Unsafe net (place can hold >1 token) ──────────────────────────
    print("━"*62)
    print("  NET 3: Unsafe net")
    print("━"*62)
    unsafe = PetriNet("Unsafe")
    src  = unsafe.add_place("src",  tokens=2)
    sink = unsafe.add_place("sink", tokens=0)
    ta   = unsafe.add_transition("ta")
    unsafe.add_arc(src, ta); unsafe.add_arc(ta, sink)
    # ta fires twice → sink gets 2 tokens → unsafe

    results3 = analyse(unsafe, k=1)
    print_report(unsafe, results3)
