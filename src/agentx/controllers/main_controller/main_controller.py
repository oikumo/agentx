from agentx.controllers.chat_controller.chat_controller import ChatController
from agentx.controllers.main_controller.commands_base import Command
from agentx.controllers.main_controller.commands_parser import CommandParser
from agentx.views.main_view.main_view import MainView, IMainViewPartner
from agentx.model.session.session_manager import SessionManager
from agentx.model.session.session_state_manager import SessionStateManager
from agentx.model.session.llm_petri_net_generator import LLMPetriNetGenerator


class MainController(IMainViewPartner):
    def __init__(self):
        self.commands: dict[str, Command] = {}
        self.parser = CommandParser()
        self.view = MainView(self)

        # Initialize session manager (always ensures a session exists)
        self.session_manager = SessionManager()
        self.session = self.session_manager.get_current_session()
        self.database = self.session_manager.get_database()
        
        # Initialize session state with Petri Net (session objectives)
        self.session_state: SessionStateManager = None
        self.petri_net_generator = LLMPetriNetGenerator("agentx")
        
        # Initialize session state from existing session or create new
        self._initialize_session_state()
    
    
    def _initialize_session_state(self):
        """Initialize or restore session state from user prompt."""
        # Session state will be created when first user query is received
        # This allows the LLM to generate the Petri Net from the actual prompt
        pass
    
    def handle_user_query(self, query: str):
        """
        Process user query and create/update session state with Petri Net.
        
        This is the main entry point for integrating session objectives
        driven by Petri Nets generated from user prompts.
        
        The LLM dynamically creates the Petri Net structure based on the query.
        The generated Petri Net is saved to a file with timestamp.
        
        Args:
            query: User's natural language query
        """
        try:
            # Generate custom Petri Net from user prompt using LLM
            self.session_state = self.petri_net_generator.generate_from_prompt(query)
            
            # Get initial state
            state = self.session_state.get_state()
            
            # Display initial state to user
            self.view.print_response(f"📋 Objective: {state.objective}")
            self.view.print_response(f"🔧 Workflow Type: LLM-generated")
            self.view.print_response(f"🎯 Status: {state.context.get('objective_status', 'pending')}")
            
            enabled = state.context.get('enabled_transitions', [])
            if enabled:
                self.view.print_response(f"✅ Available actions: {', '.join(enabled)}")
            
            # Show LLM reasoning if available
            reasoning = state.context.get('llm_reasoning', '')
            if reasoning:
                self.view.print_response(f"💡 Workflow design: {reasoning}")
            
            # Save to file with timestamp
            filepath = self.petri_net_generator.save_to_file(self.session_state)
            self.view.print_response(f"💾 Saved Petri Net to: {filepath}")
            
        except Exception as e:
            # If Petri Net generation fails, continue with normal processing
            self.view.print_response_error(f"Session state setup: {str(e)}")
    
    
    def showChat(self, query: str | None):
        self.chat_controller = ChatController()
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
