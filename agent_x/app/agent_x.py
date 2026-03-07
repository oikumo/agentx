from typing import TYPE_CHECKING

from agent_x.applications.chat_app.chat_app import ChatApp
from agent_x.applications.repl_app.replapp import ReplApp
from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp
from agent_x.applications.web_ingestion_app.tavily import WebExtract
from agent_x.app.configuration.configuration import AgentXConfiguration, AppType

if TYPE_CHECKING:
    from langchain_core.vectorstores import VectorStore


class AgentX:
    def __init__(self):
        self.llms: list[str] = []
        self.configuration: AgentXConfiguration = AgentXConfiguration()
        self.vectorstore: "VectorStore | None" = None
        self.tav: WebExtract | None = None

    def run(self):
        match self.configuration.app:
            case AppType.REPL:
                app = ReplApp()
            case AppType.CHAT:
                app = ChatApp()
            case AppType.WEB_INGESTION:
                if self.vectorstore is None or self.tav is None:
                    raise ValueError(
                        "WEB_INGESTION app requires vectorstore and tav to be set. "
                        "Set them before running: agentx.vectorstore = ...; agentx.tav = ..."
                    )
                app = WebIngestionApp(vectorstore=self.vectorstore, tav=self.tav)
        app.run()

    def configure(self):
        self.llms.append(str(len(self.llms)))
