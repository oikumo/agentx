from dotenv import load_dotenv

from agent_x.repl_app.replapp import ReplApp

load_dotenv()

if __name__ == "__main__":
    app = ReplApp()
    app.run()
