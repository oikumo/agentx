from agent_x.app_repl.app import App
from dotenv import load_dotenv


load_dotenv()

if __name__ == "__main__":
    app = App()
    app.run()
