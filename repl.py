from agent_x.app_repl.replapp import ReplApp
from dotenv import load_dotenv


load_dotenv()

if __name__ == "__main__":
    app = ReplApp()
    app.run()
