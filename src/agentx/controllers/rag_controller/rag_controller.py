from agentx.views.rag_view.rag_view import RagView, RagViewPartner
from agentx.views.ui.ui_console import UIConsole


class RagController(RagViewPartner):
    def __init__(self):
        self.view = RagView(self, UIConsole())

    def show(self):
        self.view.show()



    def close(self) -> None:
        self.view.print_message("close")

        """
        site_url = arguments[0]

        rag = Rag()
        rag.web_ingestion(site_url, self.controller.session_controller.get_directory_rag())

        return CommandResultLogInfo(["Success"])
        """

