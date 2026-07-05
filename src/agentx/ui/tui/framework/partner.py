"""Abstract-Partner registration helper for the TUI framework.

Textual's ``_MessagePumpMeta`` conflicts with :class:`abc.ABCMeta`, so TUI
screens cannot inherit ``ABC`` directly.  Screens therefore register *virtually*
against their Abstract-Partner ABC via ``ABC.register``.  This module wraps that
call so it is (a) idempotent and (b) not copy-pasted across every screen.

Design: ``design_001_tui_framework.md`` §3.1.
Operation spec: ``operation_spec_001_tui_framework.md`` O10.
"""

from __future__ import annotations


def register_partner(abc_cls: type, screen_cls: type) -> None:
    """Register ``screen_cls`` as a virtual subclass of ``abc_cls`` (an ABC).

    Works around the metaclass conflict between Textual's ``_MessagePumpMeta``
    and ``abc.ABCMeta`` — Textual screens cannot inherit ``ABC``, so they
    register virtually.

    Idempotent: re-registering an already-registered screen is a no-op.

    Args:
        abc_cls:    The Abstract-Partner ABC (e.g. ``IAgentViewPartner``).
        screen_cls: The Textual ``Screen`` subclass to register.

    Postconditions:
        - ``issubclass(screen_cls, abc_cls)`` is ``True`` (virtual).
        - ``isinstance(screen_instance, abc_cls)`` is ``True``.
    """
    if not issubclass(screen_cls, abc_cls):
        abc_cls.register(screen_cls)
