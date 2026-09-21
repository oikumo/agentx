"""
Pytest configuration (warning filters only).

The stale ``pytest_ignore_collect`` blanket exclusion for the ReAct screen
was removed in agentx_1_0_0 (release gate): the react screen ships
(``src/agentx/ui/screens/react/``), its tests live in
``tests/features/feature_018.react_screen/`` (+ console parity in
feature_024), and the two stale-API modules the exclusion hid
(``tests/controllers/react_controller/``,
``tests/views/test_react_view.py``) were deleted — they imported
``ReActController``/``ReActView`` names that never existed.
"""
import warnings

# Suppress upstream pydantic.v1 compatibility warning on Python 3.14+.
# This warning originates from langchain_core importing pydantic.v1 for
# backward compatibility — it is outside our control and adds noise to
# every test run. The actual functionality is unaffected.
warnings.filterwarnings(
    "ignore",
    message=r"Core Pydantic V1 functionality isn't compatible with Python 3\.14",
    category=UserWarning,
)
