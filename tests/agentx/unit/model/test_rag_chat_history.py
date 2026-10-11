"""Regression tests for RagChatHistory instance isolation bug fix.

Bug: RagChatHistory class attributes were shared across all instances,
causing conversation history to be disordered across sessions.
"""

from __future__ import annotations

from agentx.model.rag.query.rag_query import RagChatHistory


class TestRagChatHistoryInstanceIsolation:
    """Verify each RagChatHistory instance has independent history lists."""

    def test_independent_instances_have_separate_lists(self):
        """Creating multiple instances should not share history lists."""
        history1 = RagChatHistory()
        history2 = RagChatHistory()

        # Add data to first instance
        history1.chat_answers_history.append("Answer 1")
        history1.user_prompt_history.append("Prompt 1")
        history1.chat_history.append(("human", "Hello"))
        history1.chat_history.append(("ai", "Hi there"))

        # Second instance should be unaffected
        assert history2.chat_answers_history == []
        assert history2.user_prompt_history == []
        assert history2.chat_history == []

    def test_interleaved_sessions_maintain_isolation(self):
        """Simulate 3 concurrent chat sessions with interleaved messages."""
        session_a = RagChatHistory()
        session_b = RagChatHistory()
        session_c = RagChatHistory()

        # Session A: User asks question
        session_a.user_prompt_history.append("What is Python?")
        session_a.chat_history.append(("human", "What is Python?"))

        # Session B: User asks question
        session_b.user_prompt_history.append("What is Java?")
        session_b.chat_history.append(("human", "What is Java?"))

        # Session A: AI responds
        session_a.chat_answers_history.append("Python is a programming language...")
        session_a.chat_history.append(("ai", "Python is a programming language..."))

        # Session C: User asks question
        session_c.user_prompt_history.append("What is Rust?")
        session_c.chat_history.append(("human", "What is Rust?"))

        # Session B: AI responds
        session_b.chat_answers_history.append("Java is an object-oriented language...")
        session_b.chat_history.append(("ai", "Java is an object-oriented language..."))

        # Verify isolation
        assert session_a.user_prompt_history == ["What is Python?"]
        assert session_a.chat_answers_history == ["Python is a programming language..."]
        assert len(session_a.chat_history) == 2

        assert session_b.user_prompt_history == ["What is Java?"]
        assert session_b.chat_answers_history == ["Java is an object-oriented language..."]
        assert len(session_b.chat_history) == 2

        assert session_c.user_prompt_history == ["What is Rust?"]
        assert session_c.chat_answers_history == []
        assert len(session_c.chat_history) == 1

    def test_new_instance_starts_empty(self):
        """Each new instance should start with empty lists."""
        # Create and populate an instance
        history = RagChatHistory()
        history.chat_answers_history.append("Some answer")
        history.user_prompt_history.append("Some prompt")
        history.chat_history.append(("human", "test"))

        # Create a NEW instance - should be empty
        new_history = RagChatHistory()

        assert new_history.chat_answers_history == []
        assert new_history.user_prompt_history == []
        assert new_history.chat_history == []

    def test_mutation_on_one_instance_does_not_affect_others(self):
        """Mutating lists on one instance should not affect others."""
        h1 = RagChatHistory()
        h2 = RagChatHistory()

        # Mutate h1's lists
        h1.chat_answers_history.append("answer")
        h1.chat_history.append(("human", "q"))

        # h2 should be untouched
        assert h2.chat_answers_history == []
        assert h2.chat_history == []

        # Even after h1 mutation, h2 lists are different objects
        assert h1.chat_answers_history is not h2.chat_answers_history
        assert h1.chat_history is not h2.chat_history
        assert h1.user_prompt_history is not h2.user_prompt_history

    def test_dataclass_field_default_factory_creates_new_lists(self):
        """Verify dataclass field(default_factory=list) creates independent lists."""
        h1 = RagChatHistory()
        h2 = RagChatHistory()

        # Each field should be a different list object
        assert h1.chat_answers_history is not h2.chat_answers_history
        assert h1.user_prompt_history is not h2.user_prompt_history
        assert h1.chat_history is not h2.chat_history

        # But they should be equal (both empty initially)
        assert h1.chat_answers_history == h2.chat_answers_history == []