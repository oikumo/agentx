# Design 001: Simplified Chat Screen

**Feature:** feature_018.chat_screen_improvements  
**Type:** bug_fix  
**Date:** 2026-07-11  
**Author:** AgentX

---

## 1. Problem Statement

Feature_017 introduced conversation history persistence and a sidebar UI that created several issues:

1. **Visual clutter**: Timestamps on every message make conversations harder to read
2. **Poor visual separation**: User and agent messages don't have clear visual distinction
3. **Unnecessary complexity**: Conversation sidebar adds UI complexity that distracts from core chat functionality
4. **Feature_017 scope creep**: Added persistence features when the goal was to improve chat

## 2. Design Goals

1. **Simplicity**: Remove non-essential UI elements (timestamps, sidebar)
2. **Clarity**: Make user vs agent messages visually distinct
3. **Solidness**: Ensure the chat interface is rock-solid and reliable
4. **Minimalism**: Focus on core chat experience - send message, get response

## 3. Changes

### 3.1 ChatMessage Widget (widgets.py)

**Current issues:**
- Timestamp displayed as `[HH:MM:SS]` prefix on every message
- Visual styling is similar for user/assistant (both use borders, similar backgrounds)

**Changes:**
- Remove timestamp parameter and display
- Improve visual distinction:
  - **User messages**: Right-aligned, distinct background color (primary-darken-2), white text
  - **Assistant messages**: Left-aligned, surface background, normal text, no border
- Remove border styling to reduce visual clutter
- Add clear visual markers (e.g., "You:" prefix for user, "Assistant:" for agent)

### 3.2 ChatTUIScreen (chat_screen.py)

**Current issues:**
- Conversation sidebar with Ctrl+L toggle adds complexity
- Multiple key bindings (Ctrl+L, Ctrl+N, Ctrl+E, Ctrl+D) clutter the interface
- Sidebar widget and related logic add ~150 LOC of complexity

**Changes:**
- Remove ConversationSidebar class entirely
- Remove sidebar-related bindings (Ctrl+L, Ctrl+N, Ctrl+E, Ctrl+D)
- Remove sidebar visibility toggle logic
- Simplify layout to just messages container + input
- Keep only essential bindings: quit (q), back (escape), send (ctrl+enter)
- Remove conversation loading/persistence logic from TUI screen
- Keep persistence in controller layer (for future use if needed)

### 3.3 Controller Layer (chat_controller.py)

**Changes:**
- Keep persistence methods (start_new_conversation, load_conversation, etc.)
- These can be used programmatically or re-enabled later
- Remove view notifications that show timestamps in loaded messages

## 4. Visual Design

### 4.1 Message Styling

```
┌─────────────────────────────────────────────────────┐
│ Assistant:                                          │
│ Hello! How can I help you today?                    │
│                                                     │
│                                      You:           │
│                        I need help with my code     │
│                                                     │
│ Assistant:                                          │
│ I'd be happy to help! What's the issue?             │
└─────────────────────────────────────────────────────┘
```

### 4.2 Color Scheme

| Element | Background | Text | Alignment |
|---------|-----------|------|-----------|
| User message | $primary-darken-2 | white | right |
| Assistant message | $surface (transparent) | $text | left |

## 5. Removed Features

These features from feature_017 are **removed** to simplify the UI:

- ❌ Conversation sidebar
- ❌ Timestamps on messages
- ❌ Ctrl+L (toggle sidebar)
- ❌ Ctrl+N (new conversation via UI)
- ❌ Ctrl+E (export via UI)
- ❌ Ctrl+D (delete via UI)
- ❌ Conversation list in sidebar

These features **remain** in the controller layer for potential future use:
- ✅ Database persistence (ChatHistoryRepository)
- ✅ Conversation CRUD methods in ChatController

## 6. Testing Strategy

### 6.1 Unit Tests
- Test ChatMessage widget without timestamps
- Test visual styling (user vs assistant classes)
- Test message alignment

### 6.2 Integration Tests
- Test chat screen renders correctly
- Test message sending flow
- Test controller-view communication

### 6.3 Regression Tests
- All existing chat tests must pass
- No breaking changes to IChatView interface

## 7. MVC++ Compliance

- **View**: ChatTUIScreen, ChatMessage widget - no Model imports
- **Controller**: ChatController - handles business logic
- **Model**: ChatHistoryRepository, Conversation, ChatMessage dataclasses

All changes maintain MVC++ separation.

## 8. Success Criteria

1. [ ] ChatMessage widget has no timestamps
2. [ ] User/assistant messages have clear visual distinction
3. [ ] Sidebar removed from ChatTUIScreen
4. [ ] Simplified bindings (only q, escape, ctrl+enter)
5. [ ] All existing tests pass
6. [ ] MVC++ check: 0 errors
7. [ ] Full test suite: no new failures

---

## Appendix: Files to Modify

| File | Changes |
|------|---------|
| `src/agentx/ui/tui/framework/widgets.py` | ChatMessage: remove timestamp, improve styling |
| `src/agentx/ui/tui/screens/chat_screen.py` | Remove sidebar, simplify layout and bindings |
| `src/agentx/ui/screens/chat/chat_controller.py` | Remove timestamp display in load_conversation |
| `tests/...` | Update tests for new widget signature |