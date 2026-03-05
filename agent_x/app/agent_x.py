from agent_x.applications.repl_app.replapp import ReplApp
from agent_x.app.configuration.configuration import AgentXConfiguration


class AgentX:
    def __init__(self):
        self.llms: list[str] = []
        self.configuration: AgentXConfiguration = AgentXConfiguration()

    def run(self):
        app = ReplApp()
        app.run()

    def configure(self):
        self.llms.append(str(len(self.llms)))
