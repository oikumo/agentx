import dataclasses

from agent_x.applications.repl_app.replapp import ReplApp

class AgentX:
    llms: list[str] = []

    def __init__(self):
        pass

    def run(self):
        app = ReplApp()
        app.run()

    def configure(self):
        self.llms.append(str(len(self.llms)))