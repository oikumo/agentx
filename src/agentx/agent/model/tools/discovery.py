"""Tool discovery via stdlib ``importlib.metadata`` entry points (design §6.5).

Optional and lazy — disabled by default.  Third-party tools register via
pyproject ``[project.entry-points."agentx.tools"]`` and are instantiated here
without touching the agent core.
"""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import Any

from agentx.agent.model.tools.spec import IActuator, ISensor


def discover_tools() -> list[ISensor | IActuator]:
    """Walk the ``agentx.tools`` entry-point group and instantiate tools.

    Returns an empty list if no entry points are declared.  Errors loading a
    single entry point are swallowed (logged) so one bad plugin cannot crash
    discovery.
    """
    tools: list[ISensor | IActuator] = []
    try:
        eps = entry_points(group="agentx.tools")
    except TypeError:
        # Python <3.10 fallback (selectable entry_points)
        eps = entry_points().get("agentx.tools", [])  # type: ignore[union-attr]
    for ep in eps:
        try:
            obj: Any = ep.load()
            instance = obj() if isinstance(obj, type) else obj
            if isinstance(instance, (ISensor, IActuator)):
                tools.append(instance)
        except Exception:  # noqa: BLE001 — one bad plugin must not break others
            continue
    return tools
