from app.repl.command_line_controller.command import Command


class IMainController:
    def get_commands(self) -> list[Command]:
        pass
    def close(self):
        pass
