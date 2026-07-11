# Design Document: feature_017 — Chat Screen Improvements & History Bug Fix

## 1. Overview

**Feature ID**: `feature_017`  
**Type**: `bug_fix` + `minor_feature`  
**Priority**: High  
**Status**: Design

### 1.1 Problem Statement

Two related issues:

1. **Bug: Conversation History Disorder** — `RagChatHistory` class uses **class attributes** (shared across all instances) instead of instance attributes. All RAG chat sessions share the same history lists, causing messages from different sessions to interleave.

2. **Feature: Chat Screen Improvements** — The chat screens (both regular Chat and RAG Chat) lack:
   - Persistent conversation history across sessions
   - Clear visual separation between conversations
   - Export/import conversation capability
   - Better message formatting (timestamps, roles)

---

## 2. Root Cause Analysis

### 2.1 Bug: `RagChatHistory` Class Attributes

**File**: `src/agentx/model/rag/query/rag_query.py` (lines 12-15)

```python
class RagChatHistory:
    chat_answers_history = []      # CLASS ATTRIBUTE — SHARED!
    user_prompt_history = []       # CLASS ATTRIBUTE — SHARED!
    chat_history = []              # CLASS ATTRIBUTE — SHARED!
```

**Impact**: 
- Every `RagChatHistory()` instantiation shares the same three lists
- Multiple RAG chat sessions see each other's history
- History order becomes unpredictable when sessions interleave
- Controller's `self.rag_chat_history = self.rag.query(...)` reassigns but still uses shared lists

### 2.2 Missing Feature: Chat Persistence

Both `ChatController` and `RagChatController` only maintain in-memory history (`self.history` list). No persistence to SQLite database.

---

## 3. Solution Design

### 3.1 Bug Fix: Fix `RagChatHistory` Instance Attributes

**File**: `src/agentx/model/rag/query/rag_query.py`

```python
@dataclass
class RagChatHistory:
    chat_answers_history: list[str] = field(default_factory=list)
    user_prompt_history: list[str] = field(default_factory=list)
    chat_history: list[tuple[str, str]] = field(default_factory=list)
```

Using `@dataclass` with `field(default_factory=list)` ensures each instance gets its own independent lists.

### 3.2 Feature: Chat History Persistence Layer

Add a new module: `src/agentx/model/chat/chat_history.py`

```python
class ChatHistoryRepository:
    """SQLite-backed conversation history persistence."""
    
    def __init__(self, db_path: str = "~/.agentx/chat_history.db"):
        self.db_path = Path(db_path).expanduser()
        self._init_db()
    
    def _init_db(self):
        # conversations table: id, title, created_at, updated_at, model_provider
        # messages table: id, conversation_id, role, content, timestamp, metadata
        pass
    
    def create_conversation(self, title: str, model_provider: str) -> int:
        pass
    
    def add_message(self, conversation_id: int, role: str, content: str, metadata: dict | None = None) -> int:
        pass
    
    def get_conversation(self, conversation_id: int) -> Conversation:
        pass
    
    def get_recent_conversations(self, limit: int = 50) -> list[Conversation]:
        pass
    
    def delete_conversation(self, conversation_id: int) -> bool:
        pass
```

### 3.3 Feature: Chat Controller Integration

**Files to modify**:
- `src/agentx/ui/screens/chat/chat_controller.py` — Add `ChatHistoryRepository`, persist messages
- `src/agentx/ui/screens/rag/rag_chat_controller.py` — Add `ChatHistoryRepository`, persist RAG messages

**New methods on controllers**:
- `start_new_conversation(title: str = None)` — Create new conversation in DB
- `load_conversation(conversation_id: int)` — Load history into controller memory
- `save_current_conversation()` — Persist current in-memory history to DB
- `list_conversations()` — Return recent conversations for UI

### 3.4 Feature: Chat TUI Screen Improvements

**File**: `src/agentx/ui/tui/screens/chat_screen.py`

**New UI features**:
1. **Conversation list sidebar** (toggleable with `Ctrl+L`) — Shows recent conversations with timestamps
2. **New conversation button** (`Ctrl+N`) — Start fresh chat
3. **Message timestamps** — Show time for each message
3. **Export conversation** (`Ctrl+E`) — Save as JSON/Markdown
4. **Conversation title** — Auto-generated from first message or user-editable

**File**: `src/agentx/ui/tui/screens/rag_screen.py` (RAG chat section)

Similar improvements for RAG chat mode.

---

## 4. Data Model

### 4.1 Database Schema

```sql
-- ~/.agentx/chat_history.db
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    model_provider TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON for sources, tokens, etc.
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_updated ON conversations(updated_at DESC);
```

### 4.2 Dataclasses

```python
@dataclass
class Conversation:
    id: int
    title: str
    model_provider: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

@dataclass
class ChatMessage:
    id: int
    conversation_id: int
    role: Literal["user", "assistant", "system"]
    content: str
    metadata: dict | None
    timestamp: datetime
```

---

## 5. API Changes

### 5.1 New Public API

```python
# src/agentx/model/chat/__init__.py
from agentx.model.chat.chat_history import ChatHistoryRepository, Conversation, ChatMessage

__all__ = ["ChatHistoryRepository", "Conversation", "ChatMessage"]
```

### 5.2 Controller Changes

```python
# ChatController
class ChatController(IChatViewPartner):
    def __init__(self, view: IChatView | None = None, history_repo: ChatHistoryRepository | None = None):
        self.history_repo = history_repo or ChatHistoryRepository()
        self.current_conversation_id: int | None = None
        ...
    
    def start_new_conversation(self, title: str = None) -> int:
        """Create new conversation, return conversation_id."""
    
    def load_conversation(self, conversation_id: int) -> bool:
        """Load conversation history into memory."""
    
    def save_conversation(self) -> bool:
        """Persist current in-memory history to DB."""

# RagChatController — similar additions
```

---

## 6. UI/UX Design

### 6.1 Chat Screen Layout (Enhanced)

```
┌─────────────────────────────────────────────────────────────┐
│ Header: "AgentX Chat"                              [Ctrl+N] │
├─────────────────────────────────────────────────────────────┤
│ Conversation List (Ctrl+L toggle)  │  Messages              │
│ ┌─────────────────────────────┐   │  ┌───────────────────┐  │
│ │ 💬 Chat with Assistant      │   │  │ [10:30] You: Hi   │  │
│ │    2 min ago • 5 msgs       │   │  │ [10:30] AI: Hello!│  │
│ ├─────────────────────────────┤   │  │ [10:31] You: How  │  │
│ │ 🔍 RAG Session: docs.pdf    │   │  │ [10:31] AI: Here  │  │
│ │    1 hr ago • 12 msgs       │   │  │ ...               │  │
│ ├─────────────────────────────┤   │  └───────────────────┘  │
│ │ + New Conversation          │   │  [Input: Type here...]  │
│ └─────────────────────────────┘   └─────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Key Bindings (Extended)

| Key | Action |
|-----|--------|
| `Ctrl+N` | New conversation |
| `Ctrl+L` | Toggle conversation list sidebar |
| `Ctrl+E` | Export current conversation |
| `Ctrl+D` | Delete current conversation |
| `↑/↓` in sidebar | Navigate conversations |
| `Enter` in sidebar | Load conversation |

---

## 7. Implementation Plan

### Phase 1: Bug Fix (Priority: Critical)
1. Fix `RagChatHistory` class attributes → instance attributes (dataclass)
2. Add regression test for multi-session history isolation

### Phase 2: Persistence Layer (Priority: High)
3. Create `ChatHistoryRepository` with SQLite schema
4. Add dataclasses `Conversation`, `ChatMessage`
5. Unit tests for repository CRUD operations

### Phase 3: Controller Integration (Priority: High)
6. Integrate `ChatHistoryRepository` into `ChatController`
7. Integrate into `RagChatController`
8. Add `start_new_conversation`, `load_conversation`, `save_conversation` methods
9. Integration tests

### Phase 4: TUI Enhancements (Priority: Medium)
10. Add conversation list sidebar to `ChatTUIScreen`
11. Add message timestamps
12. Add key bindings for new actions
13. Add export functionality
14. RAG chat screen enhancements (similar)

### Phase 5: Testing & Polish
15. E2E tests for conversation persistence
16. MVC++ compliance check
17. Performance test with large history

---

## 8. Acceptance Criteria

### Bug Fix
- [ ] Multiple simultaneous RAG chat sessions maintain independent history
- [ ] History order preserved within each session
- [ ] Regression test: create 3 sessions, interleave messages, verify isolation

### Feature: Persistence
- [ ] Conversations survive app restart
- [ ] Conversation list shows title, timestamp, message count
- [ ] Load conversation restores full history in correct order
- [ ] New conversation starts with empty history

### Feature: UI
- [ ] Sidebar toggles with `Ctrl+L`
- [ ] Timestamps shown on messages
- [ ] Export saves valid JSON/Markdown
- [ ] Keyboard navigation works in sidebar

---

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| SQLite lock contention | Use WAL mode; short transactions |
| Large history performance | Paginate message loading; lazy load |
| Migration from in-memory | One-time migration on first run; backup old DB |
| MVC++ violations | Keep Model in `model/chat/`, Controller in `ui/screens/`, View in `ui/tui/screens/` |

---

## 10. Dependencies

- **New**: `dataclasses` (stdlib), `sqlite3` (stdlib), `json` (stdlib), `datetime` (stdlib)
- **Existing**: `agentx.model.ai.service.AIService` for model provider info
- **No new external dependencies** required

---

## 11. Files to Create/Modify

### New Files
- `src/agentx/model/chat/__init__.py`
- `src/agentx/model/chat/chat_history.py`
- `tests/unit/model/test_chat_history.py`
- `tests/integration/test_chat_persistence.py`

### Modified Files
- `src/agentx/model/rag/query/rag_query.py` — Fix `RagChatHistory`
- `src/agentx/ui/screens/chat/chat_controller.py` — Add persistence
- `src/agentx/ui/screens/rag/rag_chat_controller.py` — Add persistence
- `src/agentx/ui/tui/screens/chat_screen.py` — UI enhancements
- `src/agentx/ui/tui/screens/rag_screen.py` — RAG chat UI enhancements
- `src/agentx/ui/tui/framework/widgets.py` — Add timestamp to `ChatMessage` widget