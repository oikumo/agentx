"""scripts/session_inspect — normalized OpenCode session evidence (feature_131).

One stdlib-only package owns source adapters, normalized records, labels,
hierarchy, and usage accounting for real OpenCode session logs. Slice-1
surface (design_001): schema · adapter · normalize · labels · hierarchy ·
usage · collect. Slice-2: query · detail(inspect op) · trace · cli. Slice-3: profile ·
compare · exporter. Slice-4: manifest · evaluate (run gated unavailable). Slice-5: service
(Tier-2 dispatcher: closed 9-op enum, argv whitelist, bounded reads, explicit-dest
writes, run gated no_safe_launch). Read-only by contract (exports write only to explicit
destinations); every failure is a named Finding.
"""

# S6 B1 compat: canonical module is detail.py (op string inspect unchanged).
# Legacy "from session_inspect import inspect" keeps working without a
# stdlib-shadowing inspect.py on disk.
import sys as _sys
from . import detail as _detail
_sys.modules.setdefault(__name__ + ".inspect", _detail)
inspect = _detail
