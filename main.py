from dotenv import load_dotenv

from agent_x.app.agent_x import AgentX

load_dotenv()

if __name__ == "__main__":
    agent_x = AgentX()
    agent_x.run()