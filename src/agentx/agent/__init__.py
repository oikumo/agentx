"""Agent subsystem — intelligent agent framework (feature_007).

MVC++ triad:
  - Model:     ``agent.model.agent.Agent`` (facade) + subsystems
  - View:      ``agent.view`` (console + TUI)
  - Controller:``agent.controller`` (AgentController, SessionController, ToolController)

Abstract Partners live in ``agent.interfaces``; persistence in ``agent.persistence``
(stdlib sqlite3, no ORM).
"""
