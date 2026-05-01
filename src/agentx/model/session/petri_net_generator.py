"""
Dynamic Petri Net Generator for AgentX.

This module generates Petri Nets dynamically from user prompts by:
1. Extracting the objective using LLM
2. Classifying the task type
3. Selecting appropriate workflow template
4. Building the Petri Net structure
"""

from typing import Optional, Any

from agentx.model.session.workflow_templates import (
    WorkflowTemplates, 
    get_workflow_for_task, 
    get_all_templates
)
from agentx.model.session.objective_extractor_llm import extract_objective_llm, TaskType
from agentx.model.session.session_state_manager import SessionStateManager, SessionStateBuilder
from agentx.model.session.adaptive_petri_net import AdaptivePetriNet

# Lazy import to avoid circular dependencies
try:
    from langchain_core.language_models import BaseChatModel
except ImportError:
    BaseChatModel = object


class DynamicPetriNetGenerator:
    """
    Generates Petri Nets dynamically from user prompts using LLM.
    
    Usage:
        generator = DynamicPetriNetGenerator()
        session_manager = generator.generate_from_prompt(
            "I want to debug the login issue"
        )
    """
    
    def __init__(self, session_name: str = "agentx_session", llm: BaseChatModel = None):
        """
        Initialize the generator.
        
        Args:
            session_name: Name for the generated session
            llm: Optional LLM instance for objective extraction
        """
        self.session_name = session_name
        self.llm = llm
    
    def generate_from_prompt(
        self, 
        user_prompt: str, 
        custom_context: Optional[dict[str, Any]] = None
    ) -> SessionStateManager:
        """
        Generate a Petri Net session from a user prompt using LLM.
        
        Args:
            user_prompt: Natural language query from user
            custom_context: Optional context data
            
        Returns:
            SessionStateManager with generated Petri Net
        """
        # Step 1: Extract objective and classify task using LLM
        objective, task_type = extract_objective_llm(user_prompt, self.llm)
        
        # Step 2: Get workflow template
        workflow = get_workflow_for_task(task_type.value)
        
        # Step 3: Build Petri Net using builder
        builder = SessionStateBuilder(self.session_name)
        builder.set_objective(objective)
        
        # Add transitions from workflow
        for transition_name, inputs, outputs in workflow['transitions']:
            builder.add_transition(transition_name, inputs, outputs)
        
        # Build the session manager
        manager = builder.build()
        
        # Store additional metadata
        if custom_context:
            for key, value in custom_context.items():
                manager.update_context(key, value)
        
        manager.update_context('task_type', task_type.value)
        manager.update_context('workflow_name', workflow['name'])
        manager.update_context('original_prompt', user_prompt)
        
        return manager
    
    def generate_custom_workflow(
        self,
        objective: str,
        workflow: dict,
        custom_context: Optional[dict[str, Any]] = None
    ) -> SessionStateManager:
        """
        Generate a Petri Net from a custom workflow definition.
        
        Args:
            objective: The user's objective
            workflow: Workflow template dict with 'transitions' key
            custom_context: Optional context data
            
        Returns:
            SessionStateManager with custom Petri Net
        """
        builder = SessionStateBuilder(self.session_name)
        builder.set_objective(objective)
        
        # Add transitions from workflow
        for transition_name, inputs, outputs in workflow.get('transitions', []):
            builder.add_transition(transition_name, inputs, outputs)
        
        manager = builder.build()
        
        # Store metadata
        if custom_context:
            for key, value in custom_context.items():
                manager.update_context(key, value)
        
        manager.update_context('workflow_name', workflow.get('name', 'custom'))
        manager.update_context('is_custom', True)
        
        return manager


# Convenience functions

def create_session_from_prompt(
    user_prompt: str, 
    session_name: str = "agentx_session",
    llm: BaseChatModel = None
) -> SessionStateManager:
    """
    Create a session from a user prompt using LLM.
    
    Args:
        user_prompt: Natural language query from user
        session_name: Name for the session
        llm: Optional LLM instance
        
    Returns:
        SessionStateManager with generated Petri Net
    """
    generator = DynamicPetriNetGenerator(session_name, llm)
    return generator.generate_from_prompt(user_prompt)


def create_custom_session(
    objective: str,
    workflow: dict,
    session_name: str = "custom_session"
) -> SessionStateManager:
    """
    Create a session from a custom workflow.
    
    Args:
        objective: The user's objective
        workflow: Workflow template dict
        session_name: Name for the session
        
    Returns:
        SessionStateManager with custom Petri Net
    """
    generator = DynamicPetriNetGenerator(session_name)
    return generator.generate_custom_workflow(objective, workflow)


# Example usage and testing

if __name__ == "__main__":
    print("Testing LLM-based Petri Net generation...")
    
    # Test 1: Debug workflow
    print("\nTest 1: Debug workflow")
    manager = create_session_from_prompt("I want to debug the login issue")
    state = manager.get_state()
    print(f"  Objective: {state.objective}")
    print(f"  Task Type: {state.context.get('task_type', 'unknown')}")
    print(f"  Workflow: {state.context.get('workflow_name', 'unknown')}")
    print(f"  Enabled: {state.context.get('enabled_transitions', [])}")
    
    # Test 2: Analysis workflow
    print("\nTest 2: Analysis workflow")
    manager = create_session_from_prompt("Analyze the project structure")
    state = manager.get_state()
    print(f"  Objective: {state.objective}")
    print(f"  Task Type: {state.context.get('task_type', 'unknown')}")
    print(f"  Workflow: {state.context.get('workflow_name', 'unknown')}")
    print(f"  Enabled: {state.context.get('enabled_transitions', [])}")
    
    # Test 3: Implementation workflow
    print("\nTest 3: Implementation workflow")
    manager = create_session_from_prompt("Add a new feature to upload files")
    state = manager.get_state()
    print(f"  Objective: {state.objective}")
    print(f"  Task Type: {state.context.get('task_type', 'unknown')}")
    print(f"  Workflow: {state.context.get('workflow_name', 'unknown')}")
    print(f"  Enabled: {state.context.get('enabled_transitions', [])}")
