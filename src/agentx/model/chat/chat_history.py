"""Chat History Persistence Module.

Provides SQLite-backed conversation history storage for chat screens.
Database location: ~/.agentx/chat_history.db
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Conversation:
    """Represents a chat conversation."""
    id: int
    title: str
    model_provider: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


@dataclass
class ChatMessage:
    """Represents a single message in a conversation."""
    id: int
    conversation_id: int
    role: str  # "user", "assistant", "system"
    content: str
    metadata: dict[str, Any] | None
    timestamp: datetime


class ChatHistoryRepository:
    """SQLite-backed conversation history repository.
    
    Manages conversations and messages with full CRUD operations.
    Database schema:
        conversations: id, title, model_provider, created_at, updated_at
        messages: id, conversation_id, role, content, metadata, timestamp
    """
    
    DB_FILENAME = "chat_history.db"
    
    def __init__(self, db_path: str | None = None) -> None:
        """Initialize repository.
        
        Args:
            db_path: Custom database path. Defaults to ~/.agentx/chat_history.db
        """
        if db_path is None:
            default_dir = Path.home() / ".agentx"
            default_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = default_dir / self.DB_FILENAME
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Create tables and indexes if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL DEFAULT 'New Conversation',
                    model_provider TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    metadata TEXT,  -- JSON string
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated 
                ON conversations(updated_at DESC)
            """)
            conn.commit()
    
    def _row_to_conversation(self, row: tuple, msg_count: int = 0) -> Conversation:
        """Convert database row to Conversation dataclass."""
        return Conversation(
            id=row[0],
            title=row[1],
            model_provider=row[2] or "",
            created_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now(),
            updated_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
            message_count=msg_count,
        )
    
    def _row_to_message(self, row: tuple) -> ChatMessage:
        """Convert database row to ChatMessage dataclass."""
        metadata = None
        # row: id, conversation_id, role, content, metadata, timestamp
        if row[4]:
            try:
                metadata = json.loads(row[4])
            except json.JSONDecodeError:
                pass
        return ChatMessage(
            id=row[0],
            conversation_id=row[1],
            role=row[2],
            content=row[3],
            metadata=metadata,
            timestamp=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
        )
    
    def create_conversation(self, title: str = "New Conversation", model_provider: str = "") -> int:
        """Create a new conversation.
        
        Args:
            title: Conversation title
            model_provider: Name of the AI model provider
            
        Returns:
            New conversation ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO conversations (title, model_provider) VALUES (?, ?)",
                (title, model_provider)
            )
            conn.commit()
            return cursor.lastrowid or 0
    
    def add_message(
        self, 
        conversation_id: int, 
        role: str, 
        content: str, 
        metadata: dict[str, Any] | None = None
    ) -> int:
        """Add a message to a conversation.
        
        Args:
            conversation_id: Target conversation ID
            role: Message role ("user", "assistant", "system")
            content: Message content
            metadata: Optional metadata (sources, tokens, etc.)
            
        Returns:
            New message ID
        """
        meta_json = json.dumps(metadata) if metadata else None
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute(
                "INSERT INTO messages (conversation_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, meta_json)
            )
            # Update conversation timestamp
            conn.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,)
            )
            conn.commit()
            return cursor.lastrowid or 0
    
    def get_conversation(self, conversation_id: int) -> Conversation | None:
        """Get a conversation with its message count.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Conversation or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, title, model_provider, created_at, updated_at FROM conversations WHERE id = ?",
                (conversation_id,)
            ).fetchone()
            if not row:
                return None
            
            # Get message count
            count_row = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            ).fetchone()
            msg_count = count_row[0] if count_row else 0
            
            return self._row_to_conversation(row, msg_count)
    
    def get_recent_conversations(self, limit: int = 50) -> list[Conversation]:
        """Get recent conversations ordered by last update.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations (most recent first)
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT id, title, model_provider, created_at, updated_at 
                   FROM conversations 
                   ORDER BY updated_at DESC 
                   LIMIT ?""",
                (limit,)
            ).fetchall()
            
            conversations = []
            for row in rows:
                count_row = conn.execute(
                    "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
                    (row[0],)
                ).fetchone()
                msg_count = count_row[0] if count_row else 0
                conversations.append(self._row_to_conversation(row, msg_count))
            
            return conversations
    
    def get_messages(self, conversation_id: int) -> list[ChatMessage]:
        """Get all messages for a conversation in chronological order.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages ordered by timestamp
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT id, conversation_id, role, content, metadata, timestamp
                   FROM messages 
                   WHERE conversation_id = ?
                   ORDER BY timestamp ASC""",
                (conversation_id,)
            ).fetchall()
            
            return [self._row_to_message(row) for row in rows]
    
    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """Update conversation title.
        
        Args:
            conversation_id: Conversation ID
            title: New title
            
        Returns:
            True if updated, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, conversation_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_conversation(self, conversation_id: int) -> bool:
        """Delete a conversation and all its messages (CASCADE).
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_conversation_with_messages(self, conversation_id: int) -> tuple[Conversation, list[ChatMessage]] | None:
        """Get conversation and all its messages in one call.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Tuple of (Conversation, messages) or None if not found
        """
        conv = self.get_conversation(conversation_id)
        if not conv:
            return None
        messages = self.get_messages(conversation_id)
        return conv, messages
    
    def export_conversation_json(self, conversation_id: int) -> dict | None:
        """Export conversation as JSON-serializable dict.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict with conversation and messages, or None if not found
        """
        result = self.get_conversation_with_messages(conversation_id)
        if not result:
            return None
        
        conv, messages = result
        return {
            "conversation_id": conv.id,
            "title": conv.title,
            "model_provider": conv.model_provider,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in messages
            ],
        }
    
    def export_conversation_markdown(self, conversation_id: int) -> str | None:
        """Export conversation as Markdown.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Markdown string or None if not found
        """
        result = self.get_conversation_with_messages(conversation_id)
        if not result:
            return None
        
        conv, messages = result
        lines = [
            f"# {conv.title}",
            f"**Model**: {conv.model_provider or 'Unknown'}  ",
            f"**Created**: {conv.created_at.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Updated**: {conv.updated_at.strftime('%Y-%m-%d %H:%M:%S')}  ",
            "",
        ]
        
        for msg in messages:
            role_label = msg.role.capitalize()
            timestamp = msg.timestamp.strftime('%H:%M:%S')
            lines.append(f"## {timestamp} — {role_label}")
            lines.append("")
            lines.append(msg.content)
            lines.append("")
        
        return "\n".join(lines)


# Module-level singleton for convenience
_default_repo: ChatHistoryRepository | None = None


def get_default_repository() -> ChatHistoryRepository:
    """Get or create the default chat history repository."""
    global _default_repo
    if _default_repo is None:
        _default_repo = ChatHistoryRepository()
    return _default_repo