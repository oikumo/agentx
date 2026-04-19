"""
Simple Petri Net implementation in pure Python (no dependencies).

Concepts:
  - Place:      holds tokens (a non-negative integer count)
  - Transition: fires when every input place has enough tokens
  - Arc:        connects places <-> transitions with a weight (default 1)

Usage example at the bottom of this file.
"""


class Place:
    def __init__(self, name: str, tokens: int = 0):
        if tokens < 0:
            raise ValueError("Token count cannot be negative.")
        self.name = name
        self.tokens = tokens

    def __repr__(self):
        return f"Place({self.name!r}, tokens={self.tokens})"


class Transition:
    def __init__(self, name: str):
        self.name = name
        # {Place: weight}
        self.inputs: dict[Place, int] = {}
        self.outputs: dict[Place, int] = {}

    def add_input(self, place: Place, weight: int = 1):
        self.inputs[place] = weight

    def add_output(self, place: Place, weight: int = 1):
        self.outputs[place] = weight

    def is_enabled(self) -> bool:
        """A transition is enabled when every input place has >= weight tokens."""
        return all(place.tokens >= w for place, w in self.inputs.items())

    def fire(self) -> bool:
        """
        Fire the transition if enabled.
        Returns True on success, False if not enabled.
        """
        if not self.is_enabled():
            return False
        for place, w in self.inputs.items():
            place.tokens -= w
        for place, w in self.outputs.items():
            place.tokens += w
        return True

    def __repr__(self):
        return f"Transition({self.name!r})"


class PetriNet:
    def __init__(self, name: str = "PetriNet"):
        self.name = name
        self.places: dict[str, Place] = {}
        self.transitions: dict[str, Transition] = {}

    # ------------------------------------------------------------------
    # Builder helpers
    # ------------------------------------------------------------------

    def add_place(self, name: str, tokens: int = 0) -> Place:
        p = Place(name, tokens)
        self.places[name] = p
        return p

    def add_transition(self, name: str) -> Transition:
        t = Transition(name)
        self.transitions[name] = t
        return t

    def add_arc(self, src, dst, weight: int = 1):
        """
        Connect place -> transition  (input arc)
              or transition -> place (output arc).
        """
        if isinstance(src, Place) and isinstance(dst, Transition):
            dst.add_input(src, weight)
        elif isinstance(src, Transition) and isinstance(dst, Place):
            src.add_output(dst, weight)
        else:
            raise ValueError("Arc must go Place->Transition or Transition->Place.")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def enabled_transitions(self) -> list[Transition]:
        return [t for t in self.transitions.values() if t.is_enabled()]

    def marking(self) -> dict[str, int]:
        return {name: p.tokens for name, p in self.places.items()}

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def print_state(self):
        print(f"\n{'='*40}")
        print(f"  Net : {self.name}")
        print(f"{'='*40}")
        print("  Places:")
        for p in self.places.values():
            bar = "●" * p.tokens if p.tokens <= 20 else f"({p.tokens})"
            print(f"    {p.name:<18} {bar or '∅'}")
        enabled = [t.name for t in self.enabled_transitions()]
        print("  Enabled transitions:", enabled if enabled else "none")
        print(f"{'='*40}\n")

    def print_structure(self):
        print(f"\nStructure of '{self.name}':")
        for t in self.transitions.values():
            ins  = ", ".join(f"{p.name}(w={w})" for p, w in t.inputs.items())
            outs = ", ".join(f"{p.name}(w={w})" for p, w in t.outputs.items())
            print(f"  [{ins or '—'}]  -->  {t.name}  -->  [{outs or '—'}]")

    # ------------------------------------------------------------------
    # Interactive REPL
    # ------------------------------------------------------------------

    def run_interactive(self):
        print(f"\nInteractive Petri Net simulation — '{self.name}'")
        print("Commands:  fire <name>  |  step  |  state  |  quit\n")
        self.print_state()
        while True:
            try:
                cmd = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0].lower()

            if action == "quit":
                print("Bye!")
                break

            elif action == "state":
                self.print_state()

            elif action == "step":
                enabled = self.enabled_transitions()
                if not enabled:
                    print("  No transitions are enabled.")
                else:
                    t = enabled[0]
                    t.fire()
                    print(f"  Fired: {t.name}")
                    self.print_state()

            elif action == "fire" and len(parts) == 2:
                tname = parts[1]
                if tname not in self.transitions:
                    print(f"  Unknown transition '{tname}'.")
                else:
                    t = self.transitions[tname]
                    if t.fire():
                        print(f"  Fired: {tname}")
                        self.print_state()
                    else:
                        print(f"  Transition '{tname}' is NOT enabled.")

            else:
                print("  Unknown command. Use: fire <name> | step | state | quit")


# ======================================================================
#  Example: a classic producer–buffer–consumer net
# ======================================================================

def build_producer_consumer() -> PetriNet:
    """
    Producer places a token into a shared buffer; consumer takes it.

    Places:
      ready      – producer is ready (starts with 1 token)
      buffer     – shared buffer (capacity tracked implicitly)
      idle       – consumer is idle (starts with 1 token)
      produced   – producer finished one cycle
      consumed   – consumer finished one cycle

    Transitions:
      produce    – ready  --> buffer + produced
      consume    – buffer + idle --> consumed
      reset_p    – produced --> ready         (producer loops)
      reset_c    – consumed --> idle          (consumer loops)
    """
    net = PetriNet("Producer-Consumer")

    ready    = net.add_place("ready",    tokens=1)
    buffer   = net.add_place("buffer",   tokens=0)
    idle     = net.add_place("idle",     tokens=1)
    produced = net.add_place("produced", tokens=0)
    consumed = net.add_place("consumed", tokens=0)

    produce  = net.add_transition("produce")
    consume  = net.add_transition("consume")
    reset_p  = net.add_transition("reset_p")
    reset_c  = net.add_transition("reset_c")

    net.add_arc(ready,    produce)
    net.add_arc(produce,  buffer)
    net.add_arc(produce,  produced)

    net.add_arc(buffer,   consume)
    net.add_arc(idle,     consume)
    net.add_arc(consume,  consumed)

    net.add_arc(produced, reset_p)
    net.add_arc(reset_p,  ready)

    net.add_arc(consumed, reset_c)
    net.add_arc(reset_c,  idle)

    return net


def demo_auto(net: PetriNet, steps: int = 8):
    """Fire enabled transitions automatically for a few steps."""
    print(f"\n--- Automatic demo ({steps} steps) ---")
    net.print_state()
    for i in range(steps):
        enabled = net.enabled_transitions()
        if not enabled:
            print("Deadlock – no enabled transitions.")
            break
        t = enabled[0]          # deterministic: always pick the first
        t.fire()
        print(f"Step {i+1}: fired '{t.name}'  →  marking = {net.marking()}")
    net.print_state()


if __name__ == "__main__":
    import sys

    net = build_producer_consumer()
    net.print_structure()

    if "--interactive" in sys.argv or "-i" in sys.argv:
        net.run_interactive()
    else:
        demo_auto(net, steps=8)
        print("Tip: run with -i / --interactive for a live REPL.\n")
