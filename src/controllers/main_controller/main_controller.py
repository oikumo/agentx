from controllers.main_controller.repl import Command, CommandParser


class MainController:
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()

    def get_commands(self) -> list[Command]:
        return list(self.commands.values())

    def find_command(self, key) -> Command | None:
        return self.commands.get(key)

    def add_command(self, command: Command):
        self.commands[command.key] = command

    def close(self):
        exit(0)

    def run(self):
        from views.common.console import Console
        from model.session.session import Session
        from model.session.session import SessionDatabase

        Console.log_success("Agent-X")
        Console.log_info("Type 'help' for commands, Ctrl+C to exit")
        session = Session("test_2")
        if not session.create() or not session.is_created():
            raise Exception()
        database = SessionDatabase(session)

        while True:
            try:
                user_input = input("(agent-x) > ").strip()
                if not user_input:
                    continue

                command_data = self.parser.parse(user_input)
                if not command_data:
                    continue

                command = self.find_command(command_data.key)
                if not command:
                    Console.log_error(f"Unknown command: {command_data.key}")
                    continue

                database.insert_history_entry(command_data.key)

                try:
                    result = command.run(command_data.arguments)
                    if result:
                        result.apply()

                except Exception as e:
                    Console.log_error(f"Command execution failed: {e}")

                Console.log_header("History")
                entries = database.select_history_entry()
                if entries:
                    for entry in entries:
                        Console.log_info(entry.command)

            except KeyboardInterrupt:
                Console.log_info("\nReceived interrupt, exiting...")
                break
            except EOFError:
                Console.log_info("\nEOF received, exiting...")
                break

