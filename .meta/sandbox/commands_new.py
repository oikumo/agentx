from agentx.controllers.main_controller.commands_base import Command, CommandResult
from agentx.controllers.main_controller.main_controller import MainController
from agentx.views.common.console import Console
from agentx.model.session.session_manager import SessionManager


class NewSessionResult(CommandResult):
    """Result of creating a new session."""
    
    def __init__(self, session_name: str):
        self.session_name = session_name
    
    def apply(self):
        Console.log_info(f"New session created: {self.session_name}")


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
        # Extract session name from arguments if provided
        session_name = " ".join(arguments).strip() if arguments else "default_session"
        
        try:
            # Get session manager and create new session
            session_manager = SessionManager()
            new_session = session_manager.create_new_session(session_name)
            
            return NewSessionResult(new_session.name)
            
        except Exception as e:
            Console.log_error(f"Failed to create new session: {str(e)}")
            return None
