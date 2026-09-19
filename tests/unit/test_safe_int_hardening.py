"""Wild MH10 payback probe — safe_int hardening (RED before fix)."""

from agentx.utils.utils import safe_int


def test_safe_int_str_and_int_ok():
    assert safe_int("42") == 42
    assert safe_int(" 7 ") == 7
    assert safe_int(7) == 7
    assert safe_int("-3") == -3


def test_safe_int_rejects_bool_and_float():
    assert safe_int(True) is None
    assert safe_int(False) is None
    assert safe_int(3.7) is None
    assert safe_int(3.0) is None


def test_safe_int_rejects_junk():
    assert safe_int("") is None
    assert safe_int(None) is None
    assert safe_int("12.0") is None
    assert safe_int("0x10") is None
    assert safe_int("abc") is None
