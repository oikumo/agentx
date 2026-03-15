from typing import Any, Protocol, runtime_checkable
from agent_x.app.configuration.configuration import AgentXConfiguration

@runtime_checkable
class IApp(Protocol):
    def run(self) -> Any: ...


class AgentX:
    def __init__(
        self,
        configuration: AgentXConfiguration | None = None,
        app: IApp | None = None,
    ):
        self.llms: list[str] = []
        self.configuration = configuration or AgentXConfiguration()
        self._app = app

    def configure(self):
        self.llms.append(str(len(self.llms)))

    def run(self):
        if self._app is None:
            raise ValueError(
                "No app set. Use agentx.set_app(YourApp()) before running."
            )
        self._app.run()
