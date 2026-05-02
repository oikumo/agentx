from __future__ import annotations
from typing import Optional
import os

from agentx.controllers.main_controller.commands_base import Command, CommandResult
from agentx.controllers.main_controller.main_controller import MainController
from agentx.common.utils import clear_console, safe_int
from agentx.services.rag.rag import Rag
from agentx.views.common.console import Console
from agentx.model.session.session_manager import get_session_manager


class CommandResultLogInfo(CommandResult):
    def __init__(self, messages: list[str]):
        self._messages = messages

    def apply(self):
        for message in self._messages:
            Console.log_info(message)


class CommandResultPrint(CommandResult):
    def __init__(self, message: str):
        self._message = message

    def apply(self):
        Console.log_info(self._message)


class QuitCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Exit Agent-X")
        self.controller = controller

    def run(self, arguments: list[str]):
        Console.log_info("QUIT COMMAND")
        self.controller.close()


class ClearCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Clear the output screen")
        self.controller = controller

    def run(self, arguments: list[str]):
        clear_console()

class HistoryCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show commands history")
        self.controller = controller

    def run(self, arguments: list[str]):
        commands: list[str] = []
        for command in self.controller.commands_history()[:-1]:
            commands.append(f"{command}")
        return CommandResultLogInfo(commands)

class HelpCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show available commands")
        self.controller = controller

    def run(self, arguments: list[str]):
        commands: list[str] = []
        for command in self.controller.get_commands():
            commands.append(f"{command.key} - {command.description}")
        return CommandResultLogInfo(commands)


class RagWebIngestion(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="RAG web ingestion of URL: <url>")
        self.controller = controller

    def run(self, arguments: list[str]):
        if len(arguments) != 1:
            Console.log_warning("invalid command")
            return None

        site_url = arguments[0]

        rag = Rag(
            self.controller.session_manager,
            self.controller.ai_service
        )
        rag.web_ingestion(site_url)

        return CommandResultLogInfo(["Success"])

class SumCommand(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Add two integers: sum <a> <b>")
        self.controller = controller

    def run(self, arguments: list[str]):
        match arguments:
            case (x, y):
                if safe_int(x) is not None and safe_int(y) is not None:
                    result = str(int(x) + int(y))
                    return CommandResultPrint(result)
                else:
                    Console.log_warning("invalid params for sum command")
            case _:
                Console.log_warning("invalid command")
        return None


class AIChat(Command):
    def __init__(self, key: str, controller: MainController):
        super().__init__(
            key,
            description="Start an AI chat session: chat <query>, chat --model <model> <query>, or chat (interactive loop)",
        )
        self.controller = controller

    def run(self, arguments: list[str]) -> None:
        model_name, query = self.parse_chat_arguments(arguments)
        self.controller.showChat(query)

    @staticmethod
    def parse_chat_arguments(arguments: list[str]) -> tuple[str | None, str]:
        model: str | None = None
        query_parts: list[str] = []
        i = 0
        while i < len(arguments):
            if arguments[i] == "--model":
                if i + 1 < len(arguments):
                    model = arguments[i + 1]
                    i += 2
                else:
                    i += 1
            else:
                query_parts.append(arguments[i])
                i += 1
        query = " ".join(query_parts)
        return model, query


class NewSessionResult(CommandResult):
    """Result of creating a new session."""
    
    def __init__(self, session_name: str, message: str):
        self.session_name = session_name
        self.message = message
    
    def apply(self):
        Console.log_info(self.message)


class NewCommand(Command):
    """
    Command to create a new session.

    Usage: new [session_name]
    If no name is provided, a default session name will be used.
    """

    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Create a new session: new [name]")
        self.controller = controller

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        session_name = " ".join(arguments).strip() if arguments else f"session_default"

        try:
            session_manager = get_session_manager()
            new_session = session_manager.create_new_session(session_name)
            return NewSessionResult(new_session.name, f"New session created: {new_session.name}")

        except Exception as e:
            Console.log_error(f"Failed to create new session: {str(e)}")
            return None


class PetriNetStatusCommand(Command):
    """
    Command to show current Petri Net session state.

    Usage: status or petri-status
    """

    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Show current Petri Net session state: status")
        self.controller = controller

    def _get_status_display(self, status: str) -> str:
        """Get formatted status string with icon and color."""
        Console.log_error("Not implemented yet.")
        return ""

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        Console.log_error("Not implemented yet.")
        return None

class PetriNetPrintCommand(Command):
    """
    Command to pretty print the Petri Net structure.

    Usage: petri-print or pp
    """

    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Pretty print Petri Net: petri-print or pp")
        self.controller = controller

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        Console.log_error("Not implemented yet.")
        return None

class GoalCommand(Command):
    """
    Command to create a new session objective Petri Net from a user prompt.
    Each time this command is called, a new session objective Petri Net is created.

    Usage: goal {prompt}
    Example: goal Debug the login issue
    """

    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="Create new session objective Petri Net: goal {prompt}")
        self.controller = controller

    def _get_status_display(self, status: str) -> str:
        Console.log_error("Not implemented yet.")
        return ""

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        Console.log_error("Not implemented yet.")
        return None


class LSCommandResult(CommandResult):
    """Result of listing directory contents."""

    def __init__(self, files: list[str], path: str):
        self._files = sorted(files)  # Sort for consistent output
        self._path = path

    def apply(self):
        if self._files:
            Console.log_info(f"Directory: {self._path}")
            for file in self._files:
                Console.log_info(f"  {file}")
        else:
            Console.log_info(f"Directory {self._path} is empty")


class LSCommand(Command):
    """
    Command to list files in working directory.

    Usage: ls [path]
    If no path is provided, lists current directory.
    """

    def __init__(self, key: str, controller: MainController):
        super().__init__(key, description="List files in directory: ls [path]")
        self.controller = controller

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        # Determine path to list
        if arguments:
            path = arguments[0]
        else:
            path = os.getcwd()

        try:
            # List directory contents
            if os.path.exists(path) and os.path.isdir(path):
                files = os.listdir(path)
                return LSCommandResult(files, path)
            else:
                Console.log_error(f"Path does not exist or is not a directory: {path}")
                return None
        except PermissionError:
            Console.log_error(f"Permission denied: {path}")
            return None
        except Exception as e:
            Console.log_error(f"Error listing directory: {str(e)}")
            return None
