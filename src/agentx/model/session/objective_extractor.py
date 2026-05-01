"""
Objective Extractor and Task Classifier for AgentX.

This module extracts objectives from user prompts and classifies them into
task types to select appropriate workflow templates.
"""

import re
from typing import Tuple, Optional
from enum import Enum


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


class ObjectiveExtractor:
    """
    Extracts objectives from user prompts and classifies task types.
    
    Usage:
        extractor = ObjectiveExtractor()
        objective, task_type = extractor.extract("I want to debug the login issue")
        # Returns: ("debug the login issue", TaskType.DEBUG)
    """
    
    # Keywords that indicate task type
    DEBUG_KEYWORDS = [
        r'\bdebug\b', r'\bbug\b', r'\bfix\b', r'\berror\b', 
        r'\bissue\b', r'\bproblem\b', r'\bcrash\b', r'\bfail\b',
        r'\bnot working\b', r'\bbroken\b', r'\bdefect\b'
    ]
    
    ANALYSIS_KEYWORDS = [
        r'\banalyze\b', r'\banalysis\b', r'\bexamine\b', r'\breview\b',
        r'\binspect\b', r'\binvestigate\b', r'\bunderstand\b', 
        r'\bexplore\b', r'\bassess\b', r'\bevaluate\b', r'\bstructure\b'
    ]
    
    IMPLEMENTATION_KEYWORDS = [
        r'\bimplement\b', r'\bcreate\b', r'\bbuild\b', r'\bdevelop\b',
        r'\badd\b', r'\bfeature\b', r'\bfunctionality\b', r'\bwrite\b',
        r'\bcode\b', r'\bconstruct\b', r'\bdesign\b', r'\bmake\b',
        r'\bnew\b', r'\bgenerate\b'
    ]
    
    DOCUMENTATION_KEYWORDS = [
        r'\bdocument\b', r'\bdoc\b', r'\bwrite\s+docs?\b', 
        r'\bdescribe\b', r'\bexplain\b', r'\bdocument\b',
        r'\bcomment\b', r'\bannotate\b'
    ]
    
    REFACTORING_KEYWORDS = [
        r'\brefactor\b', r'\brestructure\b', r'\boptimize\b',
        r'\bimprove\b', r'\bclean\s+up\b', r'\breorganize\b',
        r'\brenaming\b', r'\brename\b'
    ]
    
    RESEARCH_KEYWORDS = [
        r'\bresearch\b', r'\bstudy\b', r'\blearn\b', 
        r'\bunderstand\b', r'\bfind\s+out\b', r'\bdetermine\b'
    ]
    
    PARALLEL_KEYWORDS = [
        r'\band\b', r'\bboth\b', r'\bmultiple\b', r'\bseveral\b',
        r'\bparallel\b', r'\bsimultaneous\b'
    ]
    
    def __init__(self):
        """Initialize the objective extractor."""
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency."""
        self.debug_pattern = re.compile('|'.join(self.DEBUG_KEYWORDS), re.IGNORECASE)
        self.analysis_pattern = re.compile('|'.join(self.ANALYSIS_KEYWORDS), re.IGNORECASE)
        self.implementation_pattern = re.compile('|'.join(self.IMPLEMENTATION_KEYWORDS), re.IGNORECASE)
        self.documentation_pattern = re.compile('|'.join(self.DOCUMENTATION_KEYWORDS), re.IGNORECASE)
        self.refactoring_pattern = re.compile('|'.join(self.REFACTORING_KEYWORDS), re.IGNORECASE)
        self.research_pattern = re.compile('|'.join(self.RESEARCH_KEYWORDS), re.IGNORECASE)
        self.parallel_pattern = re.compile('|'.join(self.PARALLEL_KEYWORDS), re.IGNORECASE)
    
    def extract(self, user_prompt: str) -> Tuple[str, TaskType]:
        """
        Extract objective and classify task type from user prompt.
        
        Args:
            user_prompt: Natural language query from user
            
        Returns:
            Tuple of (objective_string, TaskType)
        """
        # Clean the prompt
        cleaned = user_prompt.strip()
        
        # Extract the core objective
        objective = self._extract_objective_text(cleaned)
        
        # Classify the task type
        task_type = self._classify_task(cleaned)
        
        return objective, task_type
    
    def _extract_objective_text(self, prompt: str) -> str:
        """
        Extract the core objective text from a prompt.
        
        Removes common prefixes like:
        - "I want to..."
        - "I need to..."
        - "Can you..."
        - "Please..."
        - "Help me..."
        """
        # Common prefixes to remove
        prefixes = [
            r'^(i\s+want\s+to|i\s+need\s+to|i\s+would\s+like\s+to)\s+',
            r'^(can\s+you|could\s+you|will\s+you|would\s+you)\s+',
            r'^(please|plz)\s+',
            r'^(help\s+me\s+to|help\s+me)\s+',
            r'^(i\s+am\s+trying\s+to|i\s+need\s+help\s+with)\s+',
        ]
        
        result = prompt
        for prefix_pattern in prefixes:
            result = re.sub(prefix_pattern, '', result, flags=re.IGNORECASE)
        
        return result.strip()
    
    def _classify_task(self, prompt: str) -> TaskType:
        """
        Classify the task type based on keywords and patterns.
        
        Returns the most likely TaskType.
        """
        prompt_lower = prompt.lower()
        
        # Score each category
        scores = {
            TaskType.DEBUG: 0,
            TaskType.ANALYSIS: 0,
            TaskType.IMPLEMENTATION: 0,
            TaskType.DOCUMENTATION: 0,
            TaskType.REFACTORING: 0,
            TaskType.RESEARCH: 0,
        }
        
        # Check for debug keywords
        if self.debug_pattern.search(prompt_lower):
            scores[TaskType.DEBUG] += 2
        
        # Check for analysis keywords
        if self.analysis_pattern.search(prompt_lower):
            scores[TaskType.ANALYSIS] += 2
        
        # Check for implementation keywords
        if self.implementation_pattern.search(prompt_lower):
            scores[TaskType.IMPLEMENTATION] += 2
        
        # Check for documentation keywords
        if self.documentation_pattern.search(prompt_lower):
            scores[TaskType.DOCUMENTATION] += 2
        
        # Check for refactoring keywords
        if self.refactoring_pattern.search(prompt_lower):
            scores[TaskType.REFACTORING] += 2
        
        # Check for research keywords
        if self.research_pattern.search(prompt_lower):
            scores[TaskType.RESEARCH] += 2
        
        # Check for parallel task indicators
        has_parallel = bool(self.parallel_pattern.search(prompt_lower))
        if has_parallel and 'and' in prompt_lower:
            # Check if there are multiple tasks joined by 'and'
            tasks = re.split(r'\s+and\s+', prompt_lower)
            if len(tasks) > 1:
                # Boost scores for parallel if multiple distinct tasks
                for task_type in scores:
                    if scores[task_type] > 0:
                        scores[task_type] += 1
        
        # Find the highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            return TaskType.SIMPLE
        
        # Get all task types with the max score
        top_types = [t for t, s in scores.items() if s == max_score]
        
        # If tie, prefer in order: DEBUG > ANALYSIS > IMPLEMENTATION > others
        preference_order = [
            TaskType.DEBUG,
            TaskType.ANALYSIS,
            TaskType.IMPLEMENTATION,
            TaskType.REFACTORING,
            TaskType.DOCUMENTATION,
            TaskType.RESEARCH,
        ]
        
        for pref in preference_order:
            if pref in top_types:
                return pref
        
        return top_types[0] if top_types else TaskType.SIMPLE
    
    def is_parallel_task(self, prompt: str) -> bool:
        """Check if the prompt suggests a parallel/multi-agent task."""
        # Look for patterns like "analyze X and document Y"
        if ' and ' not in prompt.lower():
            return False
        
        # Check if there are multiple verbs
        verbs = self._extract_verbs(prompt)
        return len(verbs) > 1
    
    def _extract_verbs(self, text: str) -> list:
        """Extract action verbs from text."""
        all_keywords = (
            self.DEBUG_KEYWORDS + 
            self.ANALYSIS_KEYWORDS + 
            self.IMPLEMENTATION_KEYWORDS +
            self.DOCUMENTATION_KEYWORDS +
            self.REFACTORING_KEYWORDS +
            self.RESEARCH_KEYWORDS
        )
        
        found_verbs = []
        text_lower = text.lower()
        
        for keyword in all_keywords:
            if re.search(keyword, text_lower, re.IGNORECASE):
                found_verbs.append(keyword)
        
        return found_verbs


# Global instance
_extractor = None

def get_extractor() -> ObjectiveExtractor:
    """Get the global objective extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = ObjectiveExtractor()
    return _extractor


def extract_objective(user_prompt: str) -> Tuple[str, TaskType]:
    """
    Convenience function to extract objective and task type.
    
    Args:
        user_prompt: Natural language query from user
        
    Returns:
        Tuple of (objective_string, TaskType)
    """
    return get_extractor().extract(user_prompt)


def classify_task(prompt: str) -> TaskType:
    """
    Convenience function to classify task type.
    
    Args:
        prompt: Natural language query from user
        
    Returns:
        TaskType enum value
    """
    _, task_type = get_extractor().extract(prompt)
    return task_type
