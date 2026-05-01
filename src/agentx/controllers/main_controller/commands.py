from __future__ import annotations
from typing import Optional

from agentx.controllers.main_controller.commands_base import Command, CommandResult
from agentx.controllers.main_controller.main_controller import MainController
from agentx.common.utils import clear_console, safe_int
from agentx.views.common.console import Console
from agentx.model.session.session_manager import SessionManager, get_session_manager
from agentx.model.session.petri_net_visualizer import PetriNetVisualizer
from agentx.model.session.llm_petri_net_generator import LLMPetriNetGenerator


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
    
    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        try:
            # Check if session state exists
            if not hasattr(self.controller, 'session_state') or self.controller.session_state is None:
                Console.log_info("No active session state. Start with a query first.")
                return None
            
            state = self.controller.session_state.get_state()
            
            # Display state information
            lines = []
            lines.append("╔════════════════════════════════════════════════════════╗")
            lines.append("║           SESSION STATE (Petri Net)                    ║")
            lines.append("╠════════════════════════════════════════════════════════╣")
            lines.append(f"║  Objective: {state.objective[:53]:<53} ║")
            lines.append(f"║  Task Type: {state.context.get('task_type', 'unknown'):<53} ║")
            lines.append(f"║  Workflow:  {state.context.get('workflow_name', 'N/A'):<53} ║")
            lines.append(f"║  Status:    {state.context.get('objective_status', 'pending'):<53} ║")
            lines.append("╠════════════════════════════════════════════════════════╣")
            
            # Show enabled transitions
            enabled = state.context.get('enabled_transitions', [])
            if enabled:
                lines.append(f"║  Enabled Actions: {', '.join(enabled)[:35]:<35} ║")
            else:
                lines.append("║  Enabled Actions: (none)                              ║")
            
            # Show marking
            marking = state.context.get('marking', {})
            if marking:
                lines.append("║  Current Marking:                                     ║")
                for place, tokens in marking.items():
                    if tokens > 0:
                        marker_str = f"    ● {place} ({tokens})"
                    else:
                        marker_str = f"    ○ {place} (0)"
                    lines.append(f"║  {marker_str:<53} ║")
            
            lines.append("╚════════════════════════════════════════════════════════╝")
            
            return CommandResultLogInfo(lines)
            
        except Exception as e:
            Console.log_error(f"Failed to get status: {str(e)}")
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
        try:
            # Check if session state exists
            if not hasattr(self.controller, 'session_state') or self.controller.session_state is None:
                Console.log_info("No active session state. Start with a query first.")
                return None

            manager = self.controller.session_state
            visualizer = PetriNetVisualizer(manager.petri_net)

            # Generate ASCII art
            ascii_art = visualizer.to_ascii()

            return CommandResultPrint(ascii_art)

        except Exception as e:
            Console.log_error(f"Failed to print Petri Net: {str(e)}")
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
        self.generator = LLMPetriNetGenerator("agentx")

    def run(self, arguments: list[str]) -> Optional[CommandResult]:
        try:
            # Join all arguments to form the prompt
            user_prompt = " ".join(arguments).strip()
            
            if not user_prompt:
                Console.log_error("Goal requires a prompt. Usage: goal {prompt}")
                return None

            # Generate new Petri Net from the prompt
            self.controller.session_state = self.generator.generate_from_prompt(user_prompt)

            # Get the state
            state = self.controller.session_state.get_state()

            # Display state information
            lines = []
            lines.append("╔════════════════════════════════════════════════════════╗")
            lines.append("║ NEW SESSION OBJECTIVE (Petri Net) ║")
            lines.append("╠════════════════════════════════════════════════════════╣")
            lines.append(f"║ Objective: {state.objective[:53]:<53} ║")
            lines.append(f"║ Task Type: {state.context.get('task_type', 'unknown'):<53} ║")
            lines.append(f"║ Workflow: {state.context.get('workflow_name', 'N/A'):<53} ║")
            lines.append(f"║ Status: {state.context.get('objective_status', 'pending'):<53} ║")
            lines.append("╠════════════════════════════════════════════════════════╣")

            # Show enabled transitions
            enabled = state.context.get('enabled_transitions', [])
            if enabled:
                lines.append(f"║ Enabled Actions: {', '.join(enabled)[:35]:<35} ║")
            else:
                lines.append("║ Enabled Actions: (none) ║")

            # Show LLM reasoning if available
            reasoning = state.context.get('llm_reasoning', '')
            if reasoning:
                lines.append("╠════════════════════════════════════════════════════════╣")
                reasoning_short = reasoning[:53] if len(reasoning) > 53 else reasoning
                lines.append(f"║ Workflow Design: {reasoning_short:<53} ║")

            lines.append("╚════════════════════════════════════════════════════════╝")

            return CommandResultLogInfo(lines)

        except Exception as e:
            Console.log_error(f"Failed to create goal Petri Net: {str(e)}")
            return None
