from controllers.main_controller.repl import Command, CommandParser
from views.main_view.main_view import MainView, IMainViewPartner
from model.session.session import Session
from model.session.session import SessionDatabase


class MainController(IMainViewPartner):
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view = MainView(self)
        self.session = Session("test_2")
        if not self.session.create() or not self.session.is_created():
            raise Exception()
        self.database = SessionDatabase(self.session)

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


