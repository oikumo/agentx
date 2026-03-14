from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from langchain_core.vectorstores import VectorStore

from agent_x.app.configuration.configuration import AgentXConfiguration
from agent_x.applications.web_ingestion_app.tavily import WebExtract


@runtime_checkable
class IApp(Protocol):
    """Protocol defining the interface for all AgentX applications."""

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

    def set_app(self, app: IApp) -> "AgentX":
        self._app = app
        return self

    def run(self):
        if self._app is None:
            raise ValueError(
                "No app set. Use agentx.set_app(YourApp()) before running."
            )
        self._app.run()
