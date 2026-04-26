#!/usr/bin/env python3
"""
Tests for the knowledge base entry point functionality.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the knowledge base module
import knowledge_base


class TestKnowledgeBase:
    """Test suite for the knowledge base entry point."""
    
    def test_knowledge_base_imports(self):
        """Test that knowledge base module imports correctly."""
        # These should all be available
        assert hasattr(knowledge_base, 'kb_search')
        assert hasattr(knowledge_base, 'kb_ask')
        assert hasattr(knowledge_base, 'kb_add_entry')
        assert hasattr(knowledge_base, 'kb_correct')
        assert hasattr(knowledge_base, 'kb_evolve')
        assert hasattr(knowledge_base, 'kb_stats')
        
    def test_function_signatures(self):
        """Test that knowledge base functions have the expected signatures."""
        # Test that functions are callable
        assert callable(knowledge_base.kb_search)
        assert callable(knowledge_base.kb_ask)
        assert callable(knowledge_base.kb_add_entry)
        assert callable(knowledge_base.kb_correct)
        assert callable(knowledge_base.kb_evolve)
        assert callable(knowledge_base.kb_stats)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])