from dotenv import load_dotenv

from agent_x.app.agent_x import AgentX
from agent_x.applications.repl_app.replapp import ReplApp

load_dotenv()

if __name__ == "__main__":
    agent_x = AgentX()
    agent_x.set_app(ReplApp())
    agent_x.run()
