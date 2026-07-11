# Operation Specification: feature_017 — Chat Screen Improvements & History Bug Fix

## 1. Overview

This document specifies the detailed operations for implementing chat history persistence and fixing the conversation history disorder bug.

---

## 2. Operations

### 2.1 OP-001: Fix RagChatHistory Class Attributes

**Type**: Bug Fix  
**Priority**: Critical  
**Files**: `src/agentx/model/rag/query/rag_query.py`

#### 2.1.1 Current State (Broken)
```python
class RagChatHistory:
    chat_answers_history = []
    user_prompt_history = []
    chat_history = []
```

#### 2.1.2 Target State (Fixed)
```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class RagChatHistory:
    chat_answers_history: List[str] = field(default_factory=list)
    user_prompt_history: List[str] = field(default_factory=list)
    chat_history: List[Tuple[str, str]] = field(default_factory=list)
```

#### 2.1.3 Acceptance Criteria
- [ ] Each `RagChatHistory()` instance has independent lists
- [ ] Creating multiple instances does not share history
- [ ] Existing `RagQuery.ask()` method works without modification (mutates the passed instance)
- [ ] Regression test passes: 3 concurrent sessions with interleaved messages

---

### 2.2 OP-002: Create Chat History Repository

**Type**: New Module  
**Priority**: High  
**Files**: 
- `src/agentx/model/chat/__init__.py`
- `src/agentx/model/chat/chat_history.py`

#### 2.2.1 Database Path
```
~/.agentx/chat_history.db
```
(Create directory if not exists)

#### 2.2.2 Schema Operations

**Create Tables**:
```sql
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    model_provider TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON string
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
```

#### 2.2.3 Repository Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_conversation` | `(title: str, model_provider: str) -> int` | Insert new conversation, return ID |
| `add_message` | `(conversation_id: int, role: str, content: str, metadata: dict \| None) -> int` | Insert message, return ID |
| `get_conversation` | `(conversation_id: int) -> Conversation \| None` | Load full conversation with messages |
| `get_recent_conversations` | `(limit: int = 50) -> list[Conversation]` | List recent conversations for sidebar |
| `update_conversation_title` | `(conversation_id: int, title: str) -> bool` | Update title |
| `delete_conversation` | `(conversation_id: int) -> bool` | Delete conversation and messages (CASCADE) |
| `get_messages` | `(conversation_id: int) -> list[ChatMessage]` | Load messages for conversation |

#### 2.2.4 Dataclasses

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

### 2.3 OP-003: Integrate Persistence into ChatController

**Type**: Enhancement  
**Priority**: High  
**Files**: `src/agentx/ui/screens/chat/chat_controller.py`

#### 2.3.1 Constructor Changes
```python
def __init__(
    self, 
    view: IChatView | None = None,
    history_repo: ChatHistoryRepository | None = None
) -> None:
    self.history_repo = history_repo or ChatHistoryRepository()
    self.current_conversation_id: int | None = None
    ...
```

#### 2.3.2 New Methods

| Method | Signature | Behavior |
|--------|-----------|----------|
| `start_new_conversation` | `(title: str \| None = None) -> int` | Create new DB conversation, clear `self.history`, set `current_conversation_id` |
| `load_conversation` | `(conversation_id: int) -> bool` | Load messages from DB into `self.history`, set `current_conversation_id` |
| `save_conversation` | `() -> bool` | Persist `self.history` to DB (upsert messages) |
| `list_conversations` | `(limit: int = 20) -> list[Conversation]` | Delegate to repository |

#### 2.3.3 Modified Methods

- `process_user_message`: After getting response, call `save_conversation()` if `current_conversation_id` set
- `start_interactive_streaming`: If no `current_conversation_id`, auto-create conversation

---

### 2.4 OP-004: Integrate Persistence into RagChatController

**Type**: Enhancement  
**Priority**: High  
**Files**: `src/agentx/ui/screens/rag/rag_chat_controller.py`

#### 2.4.1 Constructor Changes
```python
def __init__(
    self, 
    rag_repository: RagRepository,
    history_repo: ChatHistoryRepository | None = None
) -> None:
    self.history_repo = history_repo or ChatHistoryRepository()
    self.current_conversation_id: int | None = None
    ...
```

#### 2.4.2 New Methods (same as ChatController)
- `start_new_conversation`
- `load_conversation` 
- `save_conversation`
- `list_conversations`

#### 2.4.3 Modified Methods
- `process_user_message`: After RAG query, persist user prompt + answer to DB

---

### 2.5 OP-005: Enhance ChatTUIScreen with Conversation Sidebar

**Type**: UI Enhancement  
**Priority**: Medium  
**Files**: 
- `src/agentx/ui/tui/screens/chat_screen.py`
- `src/agentx/ui/tui/framework/widgets.py` (extend ChatMessage)

#### 2.5.1 New UI Components

**ConversationSidebar** (new widget):
- Vertical list of conversations
- Each item: title, timestamp, message count
- Highlighted selection
- Keyboard navigation (↑/↓, Enter to load)

**Enhanced ChatMessage widget**:
- Add timestamp display (optional, toggleable)
- Format: `[HH:MM] Role: message`

#### 2.5.2 Layout Changes

```
Horizontal layout (when sidebar visible):
┌──────────────┬──────────────────────────────┐
│ Sidebar      │ Main Chat Area               │
│ (25% width)  │ (75% width)                  │
│              │                              │
│ Conversations│ Messages                     │
│ ─────────────│ ─────────────────────────────│
│ 💬 Chat 1    │ [10:30] You: Hello           │
│   2 min ago  │ [10:30] AI: Hi!              │
│   5 msgs     │                              │
│ ─────────────│ [Input]                      │
│ 🔍 RAG Chat  │                              │
│   1 hr ago   │                              │
│   12 msgs    │                              │
│ ─────────────│                              │
│ [+ New]      │                              │
└──────────────┴──────────────────────────────┘
```

#### 2.5.3 New Key Bindings

| Binding | Action |
|---------|--------|
| `Ctrl+L` | Toggle sidebar visibility |
| `Ctrl+N` | Start new conversation |
| `Ctrl+E` | Export current conversation |
| `Ctrl+D` | Delete current conversation (confirm) |
| `F1` | Show help with all shortcuts |

#### 2.5.4 Controller Integration

- `ChatTUIScreen` calls `controller.list_conversations()` on mount
- Sidebar selection calls `controller.load_conversation(id)`
- New conversation button calls `controller.start_new_conversation()`
- On message send, controller auto-saves

---

### 2.6 OP-006: Enhance RAG Screen Chat Mode

**Type**: UI Enhancement  
**Priority**: Medium  
**Files**: `src/agentx/ui/tui/screens/rag_screen.py`

Similar enhancements to RAG chat mode:
- Conversation history persistence via `RagChatController`
- Sidebar with RAG-specific conversations
- Message timestamps
- Export with sources included

---

### 2.7 OP-007: Export Conversation Feature

**Type**: Feature  
**Priority**: Low  
**Files**: Controllers + TUI screens

#### 2.7.1 Export Formats

**JSON**:
```json
{
  "conversation_id": 1,
  "title": "Chat with Assistant",
  "model_provider": "NVIDIA NIM",
  "created_at": "2026-07-11T10:30:00",
  "messages": [
    {"role": "user", "content": "Hello", "timestamp": "2026-07-11T10:30:05"},
    {"role": "assistant", "content": "Hi there!", "timestamp": "2026-07-11T10:30:06"}
  ]
}
```

**Markdown**:
```markdown
# Chat with Assistant
**Model**: NVIDIA NIM  
**Created**: 2026-07-11 10:30:00

## 10:30:05 — User
Hello

## 10:30:06 — Assistant
Hi there!
```

---

## 3. Test Specification

### 3.1 Unit Tests

| Test File | Coverage |
|-----------|----------|
| `tests/unit/model/test_rag_chat_history.py` | RagChatHistory instance isolation |
| `tests/unit/model/test_chat_history_repo.py` | ChatHistoryRepository CRUD |
| `tests/unit/screens/test_chat_controller.py` | Controller persistence integration |

### 3.2 Integration Tests

| Test File | Coverage |
|-----------|----------|
| `tests/integration/test_chat_persistence.py` | Full conversation lifecycle |
| `tests/integration/test_rag_chat_persistence.py` | RAG conversation persistence |

### 3.3 TUI Tests

| Test File | Coverage |
|-----------|----------|
| `tests/tui/test_chat_screen_sidebar.py` | Sidebar toggle, navigation, load |
| `tests/tui/test_chat_export.py` | Export JSON/Markdown |

---

## 4. Acceptance Checklist

### Bug Fix (OP-001)
- [ ] `RagChatHistory` uses instance attributes
- [ ] 3 concurrent sessions maintain independent history
- [ ] Interleaved messages don't leak between sessions
- [ ] Existing tests pass (no regression)

### Persistence (OP-002, OP-003, OP-004)
- [ ] SQLite DB created at `~/.agentx/chat_history.db`
- [ ] Conversations persist across app restarts
- [ ] `ChatController` and `RagChatController` both persist
- [ ] Message order preserved in DB

### UI (OP-005, OP-006)
- [ ] Sidebar toggles with `Ctrl+L`
- [ ] Sidebar shows title, time, message count
- [ ] Click/Enter on sidebar loads conversation
- [ ] Timestamps visible on messages
- [ ] `Ctrl+N` creates new conversation
- [ ] `Ctrl+E` exports to file

### Quality
- [ ] MVC++ check passes (0 errors)
- [ ] All new tests pass
- [ ] Full suite: no regressions
- [ ] Code follows OMT++ patterns