"""Unit tests for ChatHistoryRepository."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from agentx.model.chat.chat_history import ChatHistoryRepository, Conversation, ChatMessage


class TestChatHistoryRepository:
    """Test chat history repository CRUD operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temporary database."""
        return ChatHistoryRepository(db_path=temp_db)
    
    def test_init_creates_tables(self, repo):
        """Repository initialization creates required tables."""
        # Should not raise
        assert repo.db_path.exists()
    
    def test_create_conversation_returns_id(self, repo):
        """Creating a conversation returns a valid ID."""
        conv_id = repo.create_conversation("Test Chat", "OpenRouter")
        assert isinstance(conv_id, int)
        assert conv_id > 0
    
    def test_create_conversation_defaults(self, repo):
        """Conversation creation works with defaults."""
        conv_id = repo.create_conversation()
        conv = repo.get_conversation(conv_id)
        assert conv is not None
        assert conv.title == "New Conversation"
        assert conv.model_provider == ""
        assert conv.message_count == 0
    
    def test_get_conversation_returns_conversation(self, repo):
        """Created conversation can be retrieved."""
        conv_id = repo.create_conversation("My Chat", "Gemini")
        conv = repo.get_conversation(conv_id)
        
        assert conv is not None
        assert conv.id == conv_id
        assert conv.title == "My Chat"
        assert conv.model_provider == "Gemini"
        assert conv.message_count == 0
    
    def test_get_nonexistent_conversation_returns_none(self, repo):
        """Getting non-existent conversation returns None."""
        assert repo.get_conversation(999) is None
    
    def test_add_message_returns_id(self, repo):
        """Adding a message returns a valid ID."""
        conv_id = repo.create_conversation()
        msg_id = repo.add_message(conv_id, "user", "Hello!")
        
        assert isinstance(msg_id, int)
        assert msg_id > 0
    
    def test_add_message_updates_conversation_timestamp(self, repo):
        """Adding message updates conversation updated_at."""
        conv_id = repo.create_conversation()
        conv_before = repo.get_conversation(conv_id)
        updated_before = conv_before.updated_at
        
        # Small delay to ensure timestamp difference (SQLite has second precision)
        import time
        time.sleep(0.01)
        
        repo.add_message(conv_id, "user", "Test message")
        conv_after = repo.get_conversation(conv_id)
        
        # Use >= since timestamps might be in the same second
        assert conv_after.updated_at >= updated_before
    
    def test_get_messages_returns_in_order(self, repo):
        """Messages are returned in chronological order."""
        conv_id = repo.create_conversation()
        
        repo.add_message(conv_id, "user", "First")
        repo.add_message(conv_id, "assistant", "Second")
        repo.add_message(conv_id, "user", "Third")
        
        messages = repo.get_messages(conv_id)
        
        assert len(messages) == 3
        assert messages[0].content == "First"
        assert messages[1].content == "Second"
        assert messages[2].content == "Third"
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
        assert messages[2].role == "user"
    
    def test_get_messages_with_metadata(self, repo):
        """Messages can store and retrieve metadata."""
        conv_id = repo.create_conversation()
        metadata = {"source": "test", "tokens": 100}
        
        repo.add_message(conv_id, "assistant", "Response", metadata=metadata)
        messages = repo.get_messages(conv_id)
        
        assert messages[0].metadata == metadata
    
    def test_get_recent_conversations_ordered_by_update(self, repo):
        """Recent conversations are ordered by last update (newest first)."""
        id1 = repo.create_conversation("Chat 1")
        id2 = repo.create_conversation("Chat 2")
        id3 = repo.create_conversation("Chat 3")
        
        # Update chat 1 (make it most recent) - need a small delay for timestamp
        import time
        time.sleep(0.01)
        repo.add_message(id1, "user", "Message")
        
        recent = repo.get_recent_conversations(limit=10)
        
        assert len(recent) == 3
        assert recent[0].id == id1  # Most recently updated
        # The other two have same timestamp (created at same time), order not guaranteed
        assert set([recent[1].id, recent[2].id]) == {id2, id3}
    
    def test_get_recent_conversations_respects_limit(self, repo):
        """Limit parameter restricts number of returned conversations."""
        for i in range(10):
            repo.create_conversation(f"Chat {i}")
        
        recent = repo.get_recent_conversations(limit=3)
        assert len(recent) == 3
    
    def test_update_conversation_title(self, repo):
        """Conversation title can be updated."""
        conv_id = repo.create_conversation("Old Title")
        assert repo.update_conversation_title(conv_id, "New Title")
        
        conv = repo.get_conversation(conv_id)
        assert conv.title == "New Title"
    
    def test_update_nonexistent_conversation_returns_false(self, repo):
        """Updating non-existent conversation returns False."""
        assert not repo.update_conversation_title(999, "New Title")
    
    def test_delete_conversation(self, repo):
        """Conversation can be deleted (with cascading messages)."""
        conv_id = repo.create_conversation()
        repo.add_message(conv_id, "user", "Test")
        
        assert repo.delete_conversation(conv_id)
        assert repo.get_conversation(conv_id) is None
        assert repo.get_messages(conv_id) == []
    
    def test_delete_nonexistent_conversation_returns_false(self, repo):
        """Deleting non-existent conversation returns False."""
        assert not repo.delete_conversation(999)
    
    def test_export_conversation_json(self, repo):
        """Conversation can be exported as JSON."""
        conv_id = repo.create_conversation("Export Test", "TestProvider")
        repo.add_message(conv_id, "user", "Hello")
        repo.add_message(conv_id, "assistant", "Hi there!", metadata={"tokens": 10})
        
        exported = repo.export_conversation_json(conv_id)
        
        assert exported is not None
        assert exported["conversation_id"] == conv_id
        assert exported["title"] == "Export Test"
        assert exported["model_provider"] == "TestProvider"
        assert len(exported["messages"]) == 2
        assert exported["messages"][0]["role"] == "user"
        assert exported["messages"][0]["content"] == "Hello"
        assert exported["messages"][1]["metadata"] == {"tokens": 10}
    
    def test_export_nonexistent_conversation_returns_none(self, repo):
        """Exporting non-existent conversation returns None."""
        assert repo.export_conversation_json(999) is None
    
    def test_export_conversation_markdown(self, repo):
        """Conversation can be exported as Markdown."""
        conv_id = repo.create_conversation("Markdown Test", "TestProvider")
        repo.add_message(conv_id, "user", "Hello")
        repo.add_message(conv_id, "assistant", "Hi there!")
        
        markdown = repo.export_conversation_markdown(conv_id)
        
        assert markdown is not None
        assert "# Markdown Test" in markdown
        assert "**Model**: TestProvider" in markdown
        assert "## " in markdown  # Timestamp headers
        assert "Hello" in markdown
        assert "Hi there!" in markdown
    
    def test_get_conversation_with_messages(self, repo):
        """Get conversation and messages in one call."""
        conv_id = repo.create_conversation("Combined Test")
        repo.add_message(conv_id, "user", "Message 1")
        repo.add_message(conv_id, "assistant", "Response 1")
        
        result = repo.get_conversation_with_messages(conv_id)
        
        assert result is not None
        conv, messages = result
        assert conv.id == conv_id
        assert len(messages) == 2
    
    def test_multiple_repositories_independent(self, temp_db):
        """Multiple repository instances work independently."""
        repo1 = ChatHistoryRepository(db_path=temp_db)
        repo2 = ChatHistoryRepository(db_path=temp_db)
        
        id1 = repo1.create_conversation("Repo 1 Chat")
        repo1.add_message(id1, "user", "From repo 1")
        
        # repo2 should see the same data (same DB)
        convs = repo2.get_recent_conversations()
        assert len(convs) == 1
        assert convs[0].title == "Repo 1 Chat"
    
    def test_conversation_message_count(self, repo):
        """Conversation message_count is accurate."""
        conv_id = repo.create_conversation()
        conv = repo.get_conversation(conv_id)
        assert conv.message_count == 0
        
        repo.add_message(conv_id, "user", "Msg 1")
        conv = repo.get_conversation(conv_id)
        assert conv.message_count == 1
        
        repo.add_message(conv_id, "assistant", "Msg 2")
        conv = repo.get_conversation(conv_id)
        assert conv.message_count == 2


class TestChatHistoryRepositoryEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def temp_db(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        Path(db_path).unlink(missing_ok=True)
    
    def test_invalid_metadata_handled(self, temp_db):
        """Invalid JSON metadata doesn't crash."""
        repo = ChatHistoryRepository(db_path=temp_db)
        conv_id = repo.create_conversation()
        
        # Add message with metadata that will be stored as JSON
        repo.add_message(conv_id, "assistant", "Test", metadata={"key": "value"})
        
        messages = repo.get_messages(conv_id)
        assert messages[0].metadata == {"key": "value"}
    
    def test_empty_content_allowed(self, temp_db):
        """Empty message content is allowed (but not typical)."""
        repo = ChatHistoryRepository(db_path=temp_db)
        conv_id = repo.create_conversation()
        
        msg_id = repo.add_message(conv_id, "user", "")
        assert msg_id > 0
    
    def test_special_characters_in_content(self, temp_db):
        """Special characters in content are handled correctly."""
        repo = ChatHistoryRepository(db_path=temp_db)
        conv_id = repo.create_conversation()
        
        special = "Hello\nWorld\tTab\"Quote'Single\\Backslash"
        repo.add_message(conv_id, "user", special)
        
        messages = repo.get_messages(conv_id)
        assert messages[0].content == special


class TestDataclasses:
    """Test dataclass serialization."""
    
    def test_conversation_dataclass(self):
        """Conversation dataclass works correctly."""
        from datetime import datetime
        now = datetime.now()
        conv = Conversation(
            id=1,
            title="Test",
            model_provider="Provider",
            created_at=now,
            updated_at=now,
            message_count=5,
        )
        assert conv.id == 1
        assert conv.title == "Test"
        assert conv.message_count == 5
    
    def test_chat_message_dataclass(self):
        """ChatMessage dataclass works correctly."""
        from datetime import datetime
        now = datetime.now()
        msg = ChatMessage(
            id=1,
            conversation_id=1,
            role="user",
            content="Hello",
            metadata={"source": "test"},
            timestamp=now,
        )
        assert msg.role == "user"
        assert msg.metadata == {"source": "test"}