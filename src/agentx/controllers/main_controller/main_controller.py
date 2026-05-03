from agentx.controllers.chat_controller.chat_controller import ChatController
from agentx.controllers.main_controller.commands_base import Command
from agentx.controllers.main_controller.commands_parser import CommandParser
from agentx.controllers.session_controller.session_controller import SessionController
from agentx.services.ai.service import AIService
from agentx.views.main_view.main_view import MainView, IMainViewPartner


class MainController(IMainViewPartner):
    def __init__(self, ai_service: AIService):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view = MainView(self)
        self.ai_service = ai_service

        self.session_manager = SessionController()
        self.session = self.session_manager.get_current_session()
        self.database = self.session_manager.get_database()
        self._initialize_session_state()
    
    
    def _initialize_session_state(self):
        """Initialize or restore session state from user prompt."""
        # Session state will be created when first user query is received
        # This allows the LLM to generate the Petri Net from the actual prompt
        pass

    def showChat(self, query: str | None):
        self.chat_controller = ChatController(self.ai_service.openrouter_llm_provider())
        self.chat_controller.show(query)

    def run(self):
        self.view.show()

        while True:
            self.view.capture_input()

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        return self.commands.get(key)

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def commands_history(self) -> list[str]:
        history: list[str] = []

        entries = self.database.select_history_entry()
        if entries:
            for entry in entries:
                history.append(entry.command)
        return history


    def close(self):
        exit(0)

    def error(self):
        pass

    def run_command(self, user_input: str):
        command_data = self.parser.parse(user_input)
        if not command_data:
            return

        command = self.find_command(command_data.key)
        if not command:
            self.view.print_response_error(f"Unknown command: {command_data.key}")
            return

        self.database.insert_history_entry(command_data.key)

        try:
            result = command.run(command_data.arguments)
            if result:
                result.apply()

        except Exception as e:
            self.view.print_response_error(f"Command execution failed")
