"""test_omt_session_plugin_args.py — cross-source pin (design_002 §7.2).

TS OP_ARGS in .opencode/plugins/omt_session.ts must mirror
scripts/session_inspect/service.py OP_ARGS exactly; every op keeps
expected_revision (stale-rev guard); op enum stays the closed 9.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

from session_inspect.service import OPS, OP_ARGS

TS = REPO / ".opencode" / "plugins" / "omt_session.ts"


def _ts_ops():
    text = TS.read_text()
    m = re.search(r"const OPS = \[(.*?)\]", text, re.S)
    assert m, "OPS block missing in omt_session.ts"
    return re.findall(r'"([^"]+)"', m.group(1))


def _ts_op_args():
    text = TS.read_text()
    m = re.search(r"const OP_ARGS.*?\{(.*?)\n\}", text, re.S)
    assert m, "OP_ARGS block missing in omt_session.ts"
    out = {}
    for om in re.finditer(r"(\w+): \[(.*?)\]", m.group(1), re.S):
        out[om.group(1)] = re.findall(r'"([^"]+)"', om.group(2))
    return out


def test_ops_closed_nine():
    assert list(OPS) == _ts_ops()
    assert set(OPS) == {"sessions", "capture", "query", "inspect", "trace",
                        "profile", "compare", "experiment", "export"}


def test_argv_whitelist_parity():
    ts = _ts_op_args()
    assert set(ts) == set(OP_ARGS)
    for op in OP_ARGS:
        assert list(ts[op]) == list(OP_ARGS[op]), f"drift: {op}"
        assert "expected_revision" in ts[op]
