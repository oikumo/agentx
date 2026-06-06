#!/usr/bin/env python3
"""
Design pattern detector for KB MCP v4.

Heuristic-based detection of common design patterns in Python code.
"""

import ast
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from graph.models import Entity, EntityKind


@dataclass
class PatternMatch:
    """Represents a detected design pattern."""
    pattern_name: str
    confidence: float
    entity_id: str
    evidence: list[str] = field(default_factory=list)
    description: str = ""


class PatternDetector:
    """
    Heuristic-based design pattern detector.
    
    Detects the following patterns:
    - Creational: Singleton, Factory, Builder
    - Structural: Adapter, Decorator, Facade
    - Behavioral: Observer, Strategy
    - Architectural: Repository, Service, Controller
    
    Uses multiple heuristics:
    - Naming conventions
    - Method signatures
    - Class structure
    - Decorator usage
    - Inheritance patterns
    
    Usage:
        detector = PatternDetector()
        patterns = detector.detect_patterns(entities)
    """
    
    # Pattern indicators for class names
    PATTERN_NAME_INDICATORS = {
        'singleton': ['singleton', 'instance', 'registry'],
        'factory': ['factory', 'creator', 'builder', 'maker'],
        'observer': ['observer', 'listener', 'subscriber', 'watcher', 'notifier'],
        'strategy': ['strategy', 'algorithm', 'policy', 'handler'],
        'adapter': ['adapter', 'wrapper', 'proxy', 'bridge'],
        'decorator': ['decorator', 'wrapper', 'enhancer'],
        'facade': ['facade', 'manager', 'coordinator', 'orchestrator'],
        'builder': ['builder', 'constructor', 'assembler'],
        'repository': ['repository', 'dao', 'storage', 'datastore'],
        'service': ['service', 'manager', 'processor', 'engine'],
        'controller': ['controller', 'handler', 'dispatcher', 'view'],
    }
    
    # Method name indicators
    METHOD_INDICATORS = {
        'singleton': ['get_instance', 'instance', 'get'],
        'factory': ['create', 'make', 'build', 'instantiate', 'new'],
        'observer': ['notify', 'subscribe', 'unsubscribe', 'attach', 'detach', 'update'],
        'strategy': ['execute', 'run', 'process', 'handle', 'apply'],
        'adapter': ['adapt', 'convert', 'transform', 'wrap'],
        'decorator': ['decorate', 'wrap', 'enhance', 'modify'],
        'facade': ['initialize', 'setup', 'configure', 'start'],
        'builder': ['build', 'construct', 'assemble', 'create'],
        'repository': ['find', 'get', 'save', 'delete', 'list', 'query', 'fetch'],
        'service': ['process', 'execute', 'run', 'handle', 'perform'],
        'controller': ['handle', 'route', 'dispatch', 'render', 'respond'],
    }
    
    def __init__(self, min_confidence: float = 0.3):
        """
        Initialize pattern detector.
        
        Args:
            min_confidence: Minimum confidence threshold (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self.patterns: list[PatternMatch] = []
    
    def detect_patterns(self, entities: list[Entity]) -> list[PatternMatch]:
        """
        Detect all design patterns in entities.
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            List of detected patterns with confidence scores
        """
        self.patterns.clear()
        
        # Detect patterns in classes
        class_entities = [e for e in entities if e.kind == EntityKind.CLASS]
        self.detect_class_patterns(class_entities)
        
        # Detect patterns in functions/methods
        function_entities = [e for e in entities if e.kind in (EntityKind.FUNCTION, EntityKind.METHOD)]
        self.detect_function_patterns(function_entities)
        
        # Filter by confidence
        return [p for p in self.patterns if p.confidence >= self.min_confidence]
    
    def detect_class_patterns(self, classes: list[Entity]) -> list[PatternMatch]:
        """
        Detect patterns in class entities.
        
        Args:
            classes: List of class entities
            
        Returns:
            List of detected patterns
        """
        detected = []
        
        for cls in classes:
            metadata = cls.metadata or {}
            patterns_in_metadata = metadata.get('pattern', [])
            
            # Check name-based patterns
            for pattern_name, indicators in self.PATTERN_NAME_INDICATORS.items():
                confidence = self._check_name_pattern(cls.name, indicators)
                
                if confidence > 0:
                    # Boost confidence if already in metadata
                    if pattern_name in patterns_in_metadata:
                        confidence = min(1.0, confidence + 0.2)
                    
                    match = PatternMatch(
                        pattern_name=pattern_name,
                        confidence=confidence,
                        entity_id=cls.id,
                        evidence=[f"Class name contains '{pattern_name}' indicator"],
                    )
                    
                    # Check for additional evidence
                    self._check_singleton_evidence(cls, match)
                    self._check_factory_evidence(cls, match)
                    self._check_observer_evidence(cls, match)
                    self._check_strategy_evidence(cls, match)
                    
                    if match.confidence >= self.min_confidence:
                        detected.append(match)
                        self.patterns.append(match)
        
        return detected
    
    def detect_function_patterns(self, functions: list[Entity]) -> list[PatternMatch]:
        """
        Detect patterns in function/method entities.
        
        Args:
            functions: List of function/method entities
            
        Returns:
            List of detected patterns
        """
        detected = []
        
        for func in functions:
            for pattern_name, indicators in self.METHOD_INDICATORS.items():
                confidence = self._check_name_pattern(func.name, indicators)
                
                if confidence > 0:
                    match = PatternMatch(
                        pattern_name=pattern_name,
                        confidence=confidence,
                        entity_id=func.id,
                        evidence=[f"Method name '{func.name}' suggests {pattern_name}"],
                    )
                    
                    if match.confidence >= self.min_confidence:
                        detected.append(match)
                        self.patterns.append(match)
        
        return detected
    
    def _check_name_pattern(self, name: str, indicators: list[str]) -> float:
        """
        Check if name matches pattern indicators.
        
        Args:
            name: Entity name to check
            indicators: List of indicator strings
            
        Returns:
            Confidence score (0.0-1.0)
        """
        name_lower = name.lower()
        
        # Exact match
        if name_lower in indicators:
            return 0.8
        
        # Contains indicator
        for indicator in indicators:
            if indicator in name_lower:
                # Higher confidence if at the end (e.g., "UserService")
                if name_lower.endswith(indicator):
                    return 0.6
                # Lower confidence if in the middle
                return 0.4
        
        return 0.0
    
    def _check_singleton_evidence(self, cls: Entity, match: PatternMatch) -> None:
        """Check for additional Singleton pattern evidence."""
        if match.pattern_name != 'singleton':
            return
        
        metadata = cls.metadata or {}
        methods = metadata.get('methods', [])
        
        # Look for singleton-like methods
        singleton_methods = ['get_instance', 'instance', 'get', 'new']
        for method in methods:
            method_name = method if isinstance(method, str) else method.get('name', '')
            if any(sm in method_name.lower() for sm in singleton_methods):
                match.confidence = min(1.0, match.confidence + 0.1)
                match.evidence.append(f"Has singleton-like method: {method_name}")
        
        # Check decorators
        decorators = metadata.get('decorators', [])
        if 'classmethod' in decorators or 'staticmethod' in decorators:
            match.confidence = min(1.0, match.confidence + 0.05)
            match.evidence.append("Has classmethod/staticmethod (possible singleton)")
    
    def _check_factory_evidence(self, cls: Entity, match: PatternMatch) -> None:
        """Check for additional Factory pattern evidence."""
        if match.pattern_name != 'factory':
            return
        
        metadata = cls.metadata or {}
        methods = metadata.get('methods', [])
        
        # Look for factory-like methods
        factory_methods = ['create', 'make', 'build', 'new', 'instantiate']
        for method in methods:
            method_name = method if isinstance(method, str) else method.get('name', '')
            if any(fm in method_name.lower() for fm in factory_methods):
                match.confidence = min(1.0, match.confidence + 0.1)
                match.evidence.append(f"Has factory method: {method_name}")
    
    def _check_observer_evidence(self, cls: Entity, match: PatternMatch) -> None:
        """Check for additional Observer pattern evidence."""
        if match.pattern_name != 'observer':
            return
        
        metadata = cls.metadata or {}
        methods = metadata.get('methods', [])
        
        # Look for observer-like methods
        observer_methods = ['notify', 'subscribe', 'unsubscribe', 'attach', 'detach', 'update', 'on_', 'emit']
        for method in methods:
            method_name = method if isinstance(method, str) else method.get('name', '')
            if any(om in method_name.lower() or method_name.startswith('on_') or method_name.startswith('emit_') 
                   for om in observer_methods):
                match.confidence = min(1.0, match.confidence + 0.1)
                match.evidence.append(f"Has observer method: {method_name}")
    
    def _check_strategy_evidence(self, cls: Entity, match: PatternMatch) -> None:
        """Check for additional Strategy pattern evidence."""
        if match.pattern_name != 'strategy':
            return
        
        metadata = cls.metadata or {}
        
        # Check for ABC (Abstract Base Class)
        if 'abstract_base' in metadata.get('pattern', []):
            match.confidence = min(1.0, match.confidence + 0.15)
            match.evidence.append("Is abstract base class (strategy interface)")
        
        # Check for execute/handle methods
        methods = metadata.get('methods', [])
        for method in methods:
            method_name = method if isinstance(method, str) else method.get('name', '')
            if method_name in ['execute', 'handle', 'process', 'apply', 'run']:
                match.confidence = min(1.0, match.confidence + 0.1)
                match.evidence.append(f"Has strategy method: {method_name}")
    
    def get_patterns_by_entity(self, entity_id: str) -> list[PatternMatch]:
        """
        Get all patterns detected for a specific entity.
        
        Args:
            entity_id: Entity ID to look up
            
        Returns:
            List of patterns for that entity
        """
        return [p for p in self.patterns if p.entity_id == entity_id]
    
    def get_patterns_by_type(self, pattern_name: str) -> list[PatternMatch]:
        """
        Get all detections of a specific pattern type.
        
        Args:
            pattern_name: Name of the pattern (e.g., 'singleton')
            
        Returns:
            List of matches for that pattern
        """
        return [p for p in self.patterns if p.pattern_name == pattern_name]
    
    def get_high_confidence_patterns(self, threshold: float = 0.7) -> list[PatternMatch]:
        """
        Get patterns above confidence threshold.
        
        Args:
            threshold: Confidence threshold (0.0-1.0)
            
        Returns:
            List of high-confidence patterns
        """
        return [p for p in self.patterns if p.confidence >= threshold]
    
    def summarize_patterns(self) -> dict[str, int]:
        """
        Get summary of detected patterns.
        
        Returns:
            Dictionary mapping pattern name to count
        """
        summary: dict[str, int] = {}
        for pattern in self.patterns:
            summary[pattern.pattern_name] = summary.get(pattern.pattern_name, 0) + 1
        return summary
    
    def get_pattern_statistics(self) -> dict:
        """
        Get detailed statistics about detected patterns.
        
        Returns:
            Dictionary with pattern statistics
        """
        by_confidence = {
            'high': [p for p in self.patterns if p.confidence >= 0.7],
            'medium': [p for p in self.patterns if 0.5 <= p.confidence < 0.7],
            'low': [p for p in self.patterns if p.confidence < 0.5],
        }
        
        return {
            'total_patterns': len(self.patterns),
            'by_confidence': {k: len(v) for k, v in by_confidence.items()},
            'by_type': self.summarize_patterns(),
            'average_confidence': sum(p.confidence for p in self.patterns) / len(self.patterns) if self.patterns else 0.0,
        }