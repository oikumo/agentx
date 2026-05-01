"""
LLM-based Objective Extractor and Task Classifier for AgentX.

This module uses an LLM to extract objectives from user prompts and classify them
into task types to select appropriate workflow templates.
"""

import json
import re
from typing import Tuple, Optional, Dict, Any
from enum import Enum

from agentx.services.ai.services import cloud_llm_provider

# Lazy import to avoid circular dependencies
try:
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    BaseChatModel = object
    HumanMessage = None
    SystemMessage = None


class TaskType(Enum):
    """Enumeration of supported task types."""
    DEBUG = "debug"
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    DOCUMENTATION = "documentation"
    REFACTORING = "refactoring"
    RESEARCH = "research"
    PARALLEL = "parallel"
    SIMPLE = "simple"
    UNKNOWN = "unknown"


# Fallback patterns if LLM fails
FALLBACK_PATTERNS = {
    TaskType.DEBUG: [r'\bdebug\b', r'\bbug\b', r'\bfix\b', r'\berror\b', r'\bissue\b', r'\bproblem\b'],
    TaskType.ANALYSIS: [r'\banalyze\b', r'\banalysis\b', r'\bexamine\b', r'\breview\b', r'\binvestigate\b', r'\bstructure\b'],
    TaskType.IMPLEMENTATION: [r'\bimplement\b', r'\bcreate\b', r'\bbuild\b', r'\bdevelop\b', r'\badd\b', r'\bfeature\b', r'\bnew\b'],
    TaskType.DOCUMENTATION: [r'\bdocument\b', r'\bdoc\b', r'\bwrite\s+docs', r'\bdescribe\b'],
    TaskType.REFACTORING: [r'\brefactor\b', r'\brestructure\b', r'\boptimize\b', r'\bimprove\b'],
    TaskType.RESEARCH: [r'\bresearch\b', r'\bstudy\b', r'\blearn\b', r'\bunderstand\b'],
}


class LLMObjectiveExtractor:
    """
    LLM-based objective extractor and task classifier.
    
    Uses an LLM to parse user prompts and extract:
    - The core objective (what the user wants to achieve)
    - The task type (debug, analysis, implementation, etc.)
    
    Usage:
        extractor = LLMObjectiveExtractor()
        objective, task_type = await extractor.extract("I want to debug the login issue")
    """
    
    SYSTEM_PROMPT = """You are an expert at analyzing user requests and extracting objectives.

Your task is to:
1. Extract the core objective from the user's prompt
2. Classify the task into one of these categories:
   - debug: Fixing bugs, errors, or issues
   - analysis: Examining, reviewing, or understanding code/structure
   - implementation: Creating new features or functionality
   - documentation: Writing docs, descriptions, or explanations
   - refactoring: Improving or restructuring existing code
   - research: Learning or investigating a topic
   - parallel: Multiple distinct tasks combined
   - simple: Single-step queries or questions

Return your response as a JSON object with:
{
    "objective": "The core objective statement",
    "task_type": "one of: debug|analysis|implementation|documentation|refactoring|research|parallel|simple",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of classification"
}

Be concise and accurate."""

    def __init__(self, llm: BaseChatModel = None):
        """
        Initialize the LLM extractor.
        
        Args:
            llm: Optional LLM instance. If None, uses cloud provider.
        """
        self.llm = llm
        self._llm_instance = None
    
    def _get_llm(self) -> BaseChatModel:
        """Get or create LLM instance."""
        if self._llm_instance is None:
            provider = cloud_llm_provider()
            self._llm_instance = provider.create_llm()
        return self._llm_instance
    
    async def extract_async(self, user_prompt: str) -> Tuple[str, TaskType]:
        """
        Extract objective and classify task type asynchronously.
        
        Args:
            user_prompt: Natural language query from user
            
        Returns:
            Tuple of (objective_string, TaskType)
        """
        try:
            llm = self._get_llm()
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=f"User prompt: {user_prompt}")
            ]
            
            response = await llm.invoke(messages)
            result = self._parse_response(response.content)
            
            if result:
                task_type = TaskType(result['task_type'].lower())
                return result['objective'], task_type
        except Exception as e:
            print(f"LLM extraction failed: {e}, using fallback")
        
        # Fallback to pattern-based extraction
        return self._fallback_extract(user_prompt)
    
    def extract(self, user_prompt: str) -> Tuple[str, TaskType]:
        """
        Extract objective and classify task type (synchronous version).
        
        Args:
            user_prompt: Natural language query from user
            
        Returns:
            Tuple of (objective_string, TaskType)
        """
        try:
            llm = self._get_llm()
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=f"User prompt: {user_prompt}")
            ]
            
            response = llm.invoke(messages)
            result = self._parse_response(response.content)
            
            if result:
                task_type = TaskType(result['task_type'].lower())
                return result['objective'], task_type
        except Exception as e:
            print(f"LLM extraction failed: {e}, using fallback")
        
        # Fallback to pattern-based extraction
        return self._fallback_extract(user_prompt)
    
    def _parse_response(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response to extract JSON."""
        try:
            # Try to find JSON in the response
            content_str = str(content)
            
            # Look for JSON block
            json_match = re.search(r'\{[^}]+\}', content_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Validate required fields
                if 'objective' in data and 'task_type' in data:
                    return {
                        'objective': data['objective'],
                        'task_type': data['task_type'],
                        'confidence': data.get('confidence', 0.8),
                        'reasoning': data.get('reasoning', '')
                    }
        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
        
        return None
    
    def _fallback_extract(self, prompt: str) -> Tuple[str, TaskType]:
        """Fallback pattern-based extraction."""
        prompt_lower = prompt.lower().strip()
        
        # Remove common prefixes
        prefixes = [
            r'^(i\s+want\s+to|i\s+need\s+to|i\s+would\s+like\s+to)\s+',
            r'^(can\s+you|could\s+you|will\s+you)\s+',
            r'^(please|plz)\s+',
            r'^(help\s+me)\s+',
        ]
        
        objective = prompt_lower
        for prefix in prefixes:
            objective = re.sub(prefix, '', objective)
        objective = objective.strip()
        
        # Pattern matching for task type
        scores = {task_type: 0 for task_type in TaskType}
        
        for task_type, patterns in FALLBACK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    scores[task_type] += 1
        
        max_score = max(scores.values())
        if max_score == 0:
            return objective, TaskType.SIMPLE
        
        # Get first matching type with max score
        for task_type in [TaskType.DEBUG, TaskType.ANALYSIS, TaskType.IMPLEMENTATION, 
                         TaskType.REFACTORING, TaskType.DOCUMENTATION, TaskType.RESEARCH]:
            if scores[task_type] == max_score:
                return objective, task_type
        
        return objective, TaskType.SIMPLE


# Global instance
_extractor: Optional[LLMObjectiveExtractor] = None


def get_extractor(llm: BaseChatModel = None) -> LLMObjectiveExtractor:
    """Get the global LLM objective extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = LLMObjectiveExtractor(llm)
    return _extractor


def extract_objective_llm(user_prompt: str, llm: BaseChatModel = None) -> Tuple[str, TaskType]:
    """
    Extract objective using LLM.
    
    Args:
        user_prompt: Natural language query
        llm: Optional LLM instance
        
    Returns:
        Tuple of (objective, TaskType)
    """
    return get_extractor(llm).extract(user_prompt)


async def extract_objective_llm_async(user_prompt: str, llm: BaseChatModel = None) -> Tuple[str, TaskType]:
    """
    Extract objective using LLM (async version).
    
    Args:
        user_prompt: Natural language query
        llm: Optional LLM instance
        
    Returns:
        Tuple of (objective, TaskType)
    """
    return await get_extractor(llm).extract_async(user_prompt)
