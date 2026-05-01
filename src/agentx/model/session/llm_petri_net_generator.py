"""
LLM-based Dynamic Petri Net Generator for AgentX.

This module uses an LLM to dynamically generate custom Petri Net structures
based on the user's prompt, with robust JSON parsing and proper session integration.
"""

import json
import re
from typing import List, Optional, Any, Dict
from datetime import datetime
from pathlib import Path

from agentx.model.session.session_state_manager import SessionStateManager, SessionStateBuilder
from agentx.model.session.adaptive_petri_net import AdaptivePetriNet
from agentx.services.ai.services import cloud_llm_provider

# Lazy imports
try:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    BaseChatModel = object
    HumanMessage = None
    SystemMessage = None


class LLMPetriNetGenerator:
    """
    Generates custom Petri Nets dynamically using LLM.
    
    The LLM analyzes the user prompt and creates a custom workflow structure
    with appropriate places, transitions, and edges.
    """
    
    SYSTEM_PROMPT = """You are an expert at modeling workflows as Petri Nets.

Given a user's objective, you must generate a Petri Net structure that represents the workflow to achieve that objective.

A Petri Net consists of:
- **Places**: States in the workflow (e.g., "pending", "in_progress", "completed")
- **Transitions**: Actions that move from one state to another
- **Edges**: Connections showing how transitions connect places

You must return a JSON object with this exact structure:
{
    "objective": "Clear statement of what the user wants to achieve",
    "places": ["place1", "place2", "place3", ...],
    "transitions": [
        {"name": "transition_name", "from": "place1", "to": "place2"},
        ...
    ],
    "initial_place": "place1",
    "final_place": "placeN",
    "reasoning": "Brief explanation of the workflow design"
}

Rules:
1. The first place should be the starting state (e.g., "pending", "initialized")
2. The last place should be the completion state (e.g., "completed", "done")
3. Each transition connects exactly one "from" place to one "to" place
4. Place names should be descriptive (use underscores, e.g., "analysis_in_progress")
5. Transition names should be actions (verbs, e.g., "start_analysis", "complete_review")
6. Create 4-8 places for a typical workflow
7. Ensure the workflow is logical and complete

Example for "debug the login issue":
{
    "objective": "debug the login issue",
    "places": ["issue_pending", "issue_reproduced", "cause_identified", "fix_implemented", "fix_verified", "issue_resolved"],
    "transitions": [
        {"name": "reproduce", "from": "issue_pending", "to": "issue_reproduced"},
        {"name": "identify_cause", "from": "issue_reproduced", "to": "cause_identified"},
        {"name": "implement_fix", "from": "cause_identified", "to": "fix_implemented"},
        {"name": "verify_fix", "from": "fix_implemented", "to": "fix_verified"},
        {"name": "resolve", "from": "fix_verified", "to": "issue_resolved"}
    ],
    "initial_place": "issue_pending",
    "final_place": "issue_resolved",
    "reasoning": "Standard debug workflow from reproduction to resolution"
}

Now analyze this user prompt and generate the Petri Net structure. Return ONLY valid JSON."""

    def __init__(self, session_name: str = "agentx_session"):
        """
        Initialize the generator.
        
        Args:
            session_name: Name for the generated session
        """
        self.session_name = session_name
        self._llm_instance = None
    
    def _get_llm(self) -> BaseChatModel:
        """Get or create LLM instance."""
        if self._llm_instance is None:
            provider = cloud_llm_provider()
            self._llm_instance = provider.create_llm()
        return self._llm_instance
    
    def generate_from_prompt(self, user_prompt: str, max_retries: int = 3) -> SessionStateManager:
        """
        Generate a custom Petri Net from a user prompt using LLM.
        
        Args:
            user_prompt: Natural language query from user
            max_retries: Maximum number of retry attempts
            
        Returns:
            SessionStateManager with custom-generated Petri Net
        """
        # Try multiple times if parsing fails
        last_error = None
        for attempt in range(max_retries):
            try:
                # Call LLM to generate Petri Net structure
                petri_net_data = self._call_llm(user_prompt)
                
                # Validate the response
                if not self._validate_petri_net_data(petri_net_data):
                    raise ValueError("Invalid Petri Net structure from LLM")
                
                # Build the Petri Net from LLM data  
                manager = self._build_petri_net(petri_net_data)
                
                # Store metadata by adding places that hold the information as tokens
                # This integrates with the Petri Net structure
                meta = {
                    'original_prompt': user_prompt,
                    'workflow_type': 'llm_generated', 
                    'llm_reasoning': petri_net_data.get('reasoning', ''),
                    'initial_place': petri_net_data.get('initial_place', ''),
                    'final_place': petri_net_data.get('final_place', ''),
                }
                
                # Store in petri_net object for retrieval
                manager.petri_net._metadata = meta
                
                return manager
                
            except Exception as e:
                last_error = e
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    continue
        
        # If all retries failed, create a simple fallback workflow
        print(f"All LLM attempts failed, using fallback workflow")
        return self._create_fallback_workflow(user_prompt)
    
    def _call_llm(self, user_prompt: str) -> Dict[str, Any]:
        """
        Call LLM to generate Petri Net structure.
        
        Args:
            user_prompt: User's query
            
        Returns:
            Parsed JSON response from LLM
        """
        llm = self._get_llm()
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"User prompt: {user_prompt}")
        ]
        
        response = llm.invoke(messages)
        
        # Parse the response
        result = self._parse_llm_response(response.content)
        
        if not result:
            raise ValueError("Failed to parse LLM response")
        
        return result
    
    def _parse_llm_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response to extract JSON with robust error handling."""
        try:
            content_str = str(content)
            
            # Try to find JSON block
            json_match = re.search(r'\{[\s\S]*\}', content_str)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['objective', 'places', 'transitions', 'initial_place', 'final_place']
                if all(field in data for field in required_fields):
                    return data
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
        
        return None
    
    def _validate_petri_net_data(self, data: Dict[str, Any]) -> bool:
        """Validate Petri Net data structure."""
        if not all(key in data for key in ['objective', 'places', 'transitions']):
            return False
        
        if not data['places'] or not data['transitions']:
            return False
        
        # Check that transitions reference valid places
        places = set(data['places'])
        for trans in data['transitions']:
            if trans.get('from') not in places or trans.get('to') not in places:
                return False
        
        return True
    
    def _build_petri_net(self, data: Dict[str, Any]) -> SessionStateManager:
        """
        Build Petri Net from LLM-generated data.
        
        Args:
            data: Parsed LLM response
            
        Returns:
            SessionStateManager with constructed Petri Net
        """
        objective = data.get('objective', 'Custom workflow')
        places = data.get('places', [])
        transitions = data.get('transitions', [])
        
        # Create builder
        builder = SessionStateBuilder(self.session_name)
        builder.set_objective(objective)
        
        # Add transitions from LLM data
        for trans_data in transitions:
            name = trans_data.get('name', 'unknown')
            from_place = trans_data.get('from', '')
            to_place = trans_data.get('to', '')
            
            if from_place and to_place:
                builder.add_transition(name, [from_place], [to_place])
        
        # Build the manager
        manager = builder.build()
        
        return manager
    
    def _create_fallback_workflow(self, user_prompt: str) -> SessionStateManager:
        """
        Create a simple fallback workflow if LLM fails.
        
        Args:
            user_prompt: User's query
            
        Returns:
            SessionStateManager with simple workflow
        """
        builder = SessionStateBuilder(self.session_name)
        builder.set_objective(user_prompt)
        
        # Simple 3-state workflow
        builder.add_transition('start', ['pending'], ['in_progress'])
        builder.add_transition('complete', ['in_progress'], ['completed'])
        
        manager = builder.build()
        manager.update_context('original_prompt', user_prompt)
        manager.update_context('workflow_type', 'fallback')
        manager.update_context('llm_reasoning', 'LLM failed, using simple fallback workflow')
        
        return manager
    
    def save_to_session(self, manager: SessionStateManager, session_db) -> str:
        """
        Save the Petri Net to the current session's database.
        
        Args:
            manager: SessionStateManager to save
            session_db: SessionDatabase instance
            
        Returns:
            Path or identifier for saved Petri Net
        """
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state = manager.get_state()
        objective_safe = state.objective[:30].replace(' ', '_').replace('/', '_').replace('\\', '_')
        filename = f"petri_net_{timestamp}_{objective_safe}.json"
        
        # Serialize to dict
        state_dict = manager.to_dict()
        
        # Add Petri Net structure details
        petri_net = manager.petri_net
        state_dict['petri_net'] = {
            'name': petri_net.name,
            'objective': petri_net.objective,
            'places': {name: {'tokens': place.tokens} for name, place in petri_net.places.items()},
            'transitions': [
                {
                    'name': t.name,
                    'inputs': [p.name for p in t.inputs.keys()],
                    'outputs': [p.name for p in t.outputs.keys()]
                }
                for t in petri_net.transitions.values()
            ],
            'state_history': petri_net.state_history
        }
        
        # Save to session directory
        session_dir = session_db.session.directory if hasattr(session_db, 'session') else Path('.meta/sessions')
        filepath = Path(session_dir) / filename
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, indent=2, default=str)
        
        return str(filepath)


# Convenience function
def generate_petri_net_from_prompt(user_prompt: str, session_name: str = "agentx_session") -> SessionStateManager:
    """
    Generate a custom Petri Net from a user prompt.
    
    Args:
        user_prompt: Natural language query
        session_name: Name for the session
        
    Returns:
        SessionStateManager with generated Petri Net
    """
    generator = LLMPetriNetGenerator(session_name)
    return generator.generate_from_prompt(user_prompt)


# Example usage
if __name__ == "__main__":
    print("Testing LLM-based Petri Net generation...")
    
    test_prompts = [
        "Debug the database connection timeout issue",
        "Analyze the security vulnerabilities in authentication",
        "Implement a file upload feature with progress tracking",
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*70}")
        print(f"Prompt: {prompt}")
        print('='*70)
        
        try:
            manager = generate_petri_net_from_prompt(prompt)
            state = manager.get_state()
            
            print(f"✓ Objective: {state.objective}")
            print(f"✓ Workflow Type: {state.context.get('workflow_type', 'unknown')}")
            print(f"✓ Reasoning: {state.context.get('llm_reasoning', 'N/A')}")
            print(f"✓ Initial Place: {state.context.get('initial_place', 'N/A')}")
            print(f"✓ Final Place: {state.context.get('final_place', 'N/A')}")
            print(f"✓ Enabled: {state.context.get('enabled_transitions', [])}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
