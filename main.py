from dotenv import load_dotenv

from agent_x.app.app import App

load_dotenv()

if __name__ == "__main__":
    app = App()
    app.run()
