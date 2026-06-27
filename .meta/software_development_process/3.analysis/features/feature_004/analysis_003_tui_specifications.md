# ANALYSIS 003: Textual TUI Specifications

**Feature:** feature_004.modern_ui  
**Date:** 2026-06-21  
**Phase:** Analysis  
**Status:** Draft

---

## 1. Overview

This document specifies the detailed UI behavior and widget specifications for the Textual TUI implementation across all screens.

---

## 2. Textual Library Selection

### 2.1 Why Textual?

**Selected:** Textual v0.89.0+ (latest stable)

**Reasons:**
- Pure Python TUI framework
- Rich widget library (tables, progress bars, buttons, inputs)
- Reactive programming model
- CSS-like styling
- Active development and community
- Works with Python 3.14+

### 2.2 Required Dependencies

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies ...
    "textual>=0.89.0",
]
```

### 2.3 Textual Features Used

**Core Features:**
- `App` - Main application class
- `Screen` - Screen base class
- `Widget` - Base widget class
- `reactive` - Reactive attributes
- `on_mount`, `on_unmount` - Lifecycle hooks

**Widgets:**
- `Header` - Top bar with title
- `Footer` - Bottom bar with key bindings
- `StatusBar` - Session context display
- `Button` - Clickable buttons
- `Input` - Text input fields
- `DataTable` - Repository lists
- `ProgressBar` - Ingestion progress
- `RichLog` - Chat message display
- `Notification` - Toast messages

**Layout:**
- `Vertical`, `Horizontal` - Layout containers
- `Grid` - Grid layout
- CSS-like styling

---

## 3. Main Screen Specifications

### 3.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: "AgentX"                                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Welcome Panel                                          │
│  ╔══════════════════════════════════════════════════╗  │
│  ║  Welcome to AgentX                               ║  │
│  ║  Type commands or use menu options below         ║  │
│  ╚══════════════════════════════════════════════════╝  │
│                                                         │
│  Menu Options (Button Grid)                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  💬 Chat    │  │  📚 RAG     │  │  ⚙️  Help    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                         │
│  Command Input                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ (agentx) >                                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Status: Session: default | Dir: /path | Screen: Main │
│  Footer: [Q]uit [H]elp [→]Navigate                     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Widget Tree

```
MainTUIScreen
├── Header (text: "AgentX")
├── Vertical (container)
│   ├── Static (welcome panel)
│   ├── Grid (menu buttons)
│   │   ├── Button (id: "btn-chat")
│   │   ├── Button (id: "btn-rag")
│   │   └── Button (id: "btn-help")
│   └── Input (id: "cmd-input", placeholder: "(agentx) > ")
├── StatusBar
│   ├── Label (session name)
│   ├── Label (directory)
│   └── Label (screen name)
└── Footer (key bindings)
```

### 3.3 Interactions

**Button Clicks:**
- Chat button → Navigate to ChatTUIScreen
- RAG button → Navigate to RagTUIScreen
- Help button → Show help modal

**Input Field:**
- User types command
- Press Enter → Controller processes command
- Display result in notification
- Clear input field

**Keyboard Shortcuts:**
- `q` or `Q` → Quit confirmation
- `h` or `H` → Show help
- Arrow keys → Navigate buttons
- `Enter` → Activate selected button

### 3.4 State Management

**Session Context (Reactive):**
```python
class MainTUIScreen(Screen):
    session_name = reactive("default")
    working_directory = reactive("/path")
    current_screen = reactive("Main")
    
    def watch_session_name(self, new_name: str) -> None:
        self.status_bar.update_session(new_name)
```

**Updates:**
- Session changes → Auto-update status bar
- Navigation → Update "current_screen" label
- Directory change → Auto-update status bar

---

## 4. RAG Screen Specifications

### 4.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: "RAG - Retrieval Augmented Generation"         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Repository Status Panel                                │
│  ╔══════════════════════════════════════════════════╗  │
│  ║  Repository: rag_knowledge_base                  ║  │
│  ║  Status: ✅ Ready                                ║  │
│  ║  Ingested: https://example.com                   ║  │
│  ║  Documents: 42 | Database: rag.db                ║  │
│  ╚══════════════════════════════════════════════════╝  │
│                                                         │
│  Menu Options (Button Grid)                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 📁 Select    │ │ ➕ Create    │ │ 🌐 Ingest    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                    │
│  │ 💬 Chat      │ │ ← Back       │                    │
│  └──────────────┘ └──────────────┘                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Status: Session: default | Dir: /rag_kb | Screen: RAG│
│  Footer: [1-5]Select [B]ack [Q]uit                     │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Repository Selection Modal

```
┌────────────────────────────────────────────────┐
│  Select Repository                      [X]    │
├────────────────────────────────────────────────┤
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │ Repository Name          │ Status        │  │
│  ├──────────────────────────────────────────┤  │
│  │ rag_knowledge_base       │ ✅ Ready      │  │
│  │ rag_docs                 │ ✅ Ready      │  │
│  │ rag_temp                 │ ⚠️  Empty     │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  [Select]  [Create New]  [Cancel]              │
└────────────────────────────────────────────────┘
```

**DataTable Features:**
- Sortable columns
- Click to select row
- Visual status indicators
- Empty state message

### 4.3 Create Repository Modal

```
┌────────────────────────────────────────────────┐
│  Create New Repository                  [X]    │
├────────────────────────────────────────────────┤
│                                                │
│  Repository Name:                              │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ℹ️  Name must be alphanumeric + underscore   │
│  ℹ️  "rag_" prefix will be added automatically │
│                                                │
│  [Create]  [Cancel]                            │
└────────────────────────────────────────────────┘
```

**Validation:**
- Real-time validation as user types
- Show error message inline
- Disable "Create" button if invalid

### 4.4 Web Ingestion Screen

```
┌─────────────────────────────────────────────────────────┐
│  Web Ingestion                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  URL Input                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ https://example.com                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  Extraction Level                                       │
│  ○ Low (fast, 10 pages max)                            │
│  ● Mid (balanced, 50 pages max)                        │
│  ○ High (thorough, 100 pages max)                      │
│                                                         │
│  Progress                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━╺━━━━━━━  75%                 │
│  Pages: 37/50 | Chunks: 142                            │
│                                                         │
│  [Start]  [Cancel]  ← Back                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**ProgressBar Features:**
- Real-time updates during ingestion
- Show pages processed
- Show chunks created
- Cancel support

### 4.5 RAG Chat Screen

```
┌─────────────────────────────────────────────────────────┐
│  RAG Chat                                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Chat History (RichLog)                                 │
│  ╔══════════════════════════════════════════════════╗  │
│  ║  👤 User: What is RAG?                           ║  │
│  ║                                                  ║  │
│  ║  🤖 Assistant: RAG stands for Retrieval          ║  │
│  ║  Augmented Generation. It's a technique that...  ║  │
│  ║                                                  ║  │
│  ║  📚 Sources:                                     ║  │
│  ║  • https://example.com/rag-intro                 ║  │
│  ╚══════════════════════════════════════════════════╝  │
│                                                         │
│  Input                                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Type your question...                            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [Send]  ← Back                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Message Bubbles:**
- User messages: Right-aligned, blue background
- Assistant messages: Left-aligned, gray background
- Source links: Clickable, open in browser
- Streaming: Typing indicator during generation

---

## 5. Chat Screen Specifications

### 5.1 Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: "Chat"                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Chat History                                           │
│  ╔══════════════════════════════════════════════════╗  │
│  ║  👤 User: Hello                                  ║  │
│  ║                                                  ║  │
│  ║  🤖 Assistant: Hi! How can I help you today?     ║  │
│  ╚══════════════════════════════════════════════════╝  │
│                                                         │
│  Input                                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Type a message...                                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [Send]  ← Back                                         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Status: Session: default | Model: gpt-4 | Screen: Chat│
│  Footer: [Enter]Send [Esc]Back [Q]uit                  │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Message Display

**User Message Widget:**
```python
class UserMessage(Static):
    DEFAULT_CSS = """
    UserMessage {
        background: $blue;
        color: white;
        padding: 1 2;
        margin: 1 0;
        dock: right;
        width: 80%;
    }
    """
```

**Assistant Message Widget:**
```python
class AssistantMessage(Static):
    DEFAULT_CSS = """
    AssistantMessage {
        background: $gray;
        color: white;
        padding: 1 2;
        margin: 1 0;
        dock: left;
        width: 80%;
    }
    """
```

### 5.3 Streaming Response

**Typing Indicator:**
```python
class TypingIndicator(Static):
    """Animated "..." indicator"""
    
    def on_mount(self) -> None:
        self.set_interval(0.5, self.animate_dots)
    
    def animate_dots(self) -> None:
        # Cycle through ".", "..", "..."
```

**Stream Update:**
- Assistant receives chunk from LLM
- Call `chat_screen.append_to_last_message(chunk)`
- RichLog auto-scrolls to bottom
- Typing indicator removed when complete

---

## 6. Common Components

### 6.1 Status Bar (All Screens)

**Specification:**
```python
class SessionStatusBar(Static):
    """Displays session context across all screens"""
    
    # Reactive attributes
    session_name = reactive("default")
    working_directory = reactive("/path")
    current_screen = reactive("Unknown")
    
    # Auto-update on changes
    def watch_session_name(self, name: str) -> None:
        self.update_display()
```

**Display Format:**
```
Session: {session_name} | Dir: {directory} | Screen: {screen_name}
```

**Position:** Fixed at bottom, above Footer

### 6.2 Notification System

**Types:**
- `info` - Blue notification (auto-dismiss 3s)
- `success` - Green notification (auto-dismiss 3s)
- `warning` - Yellow notification (auto-dismiss 5s)
- `error` - Red notification (manual dismiss)

**Position:** Top-right corner, stack vertically

**Usage:**
```python
self.notify("Repository created successfully!", severity="information")
self.notify("Failed to connect", severity="error", timeout=None)
```

### 6.3 Modal Dialogs

**Base Structure:**
```python
class ModalScreen(Screen):
    """Base class for all modal dialogs"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("enter", "submit", "Submit"),
    ]
```

**Features:**
- Centered on screen
- Dimmed background
- Close on Escape
- Submit on Enter
- Focus management

---

## 7. Navigation Flow

### 7.1 Screen Stack

```
MainTUIScreen (root)
    ├── push → ChatTUIScreen
    │           └── pop → MainTUIScreen
    │
    └── push → RagTUIScreen
                ├── push → RepositorySelectionModal
                │           └── pop → RagTUIScreen
                ├── push → CreateRepositoryModal
                │           └── pop → RagTUIScreen
                ├── push → WebIngestionScreen
                │           └── pop → RagTUIScreen
                ├── push → RagChatScreen
                │           └── pop → RagTUIScreen
                └── pop → MainTUIScreen
```

### 7.2 Navigation Methods

**Push Screen:**
```python
self.push_screen(ChatTUIScreen(), callback=self.on_chat_closed)
```

**Pop Screen:**
```python
self.pop_screen()
```

**Callback Pattern:**
```python
def on_chat_closed(result: str) -> None:
    """Called when chat screen closes"""
    self.notify(f"Chat ended: {result}")
```

---

## 8. Key Bindings (All Screens)

### 8.1 Global Bindings

| Key | Action | Scope |
|-----|--------|-------|
| `Ctrl+Q` | Quit application | All |
| `Ctrl+H` | Show help | All |
| `Esc` | Back/Close modal | All |
| `Enter` | Submit/Activate | All |

### 8.2 Screen-Specific Bindings

**Main Screen:**
| Key | Action |
|-----|--------|
| `1` or `C` | Open Chat |
| `2` or `R` | Open RAG |
| `3` or `H` | Show Help |

**RAG Screen:**
| Key | Action |
|-----|--------|
| `1` | Select Repository |
| `2` | Create Repository |
| `3` | Web Ingestion |
| `4` | RAG Chat |
| `5` or `B` | Back to Main |

**Chat Screen:**
| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `B` | Back to Main |

---

## 9. Styling Guidelines

### 9.1 Color Scheme

```css
/* AgentX Theme */
$primary: #3B82F6;      /* Blue - primary actions */
$secondary: #10B981;    /* Green - success */
$warning: #F59E0B;      /* Yellow - warnings */
$error: #EF4444;        /* Red - errors */
$background: #1E293B;   /* Dark blue-gray - background */
$surface: #334155;      /* Lighter - panels */
$text: #F8FAFC;         /* White - text */
```

### 9.2 Consistent Styling

**Buttons:**
- Primary actions: Blue background
- Secondary actions: Gray background
- Destructive actions: Red background

**Panels:**
- Welcome/info: Blue border
- Success: Green border
- Warning: Yellow border
- Error: Red border

**Text:**
- Headers: Bold, larger font
- Body: Regular font
- Captions: Smaller, muted color

---

## 10. Performance Considerations

### 10.1 Widget Optimization

**Do:**
- Use `reactive` for auto-updates
- Batch UI updates when possible
- Use `display: none` instead of removing widgets
- Cache expensive computations

**Don't:**
- Update UI in tight loops
- Create/destroy widgets frequently
- Block event loop with long operations
- Update UI from background threads directly

### 10.2 Async Operations

**Pattern:**
```python
async def long_operation(self) -> Result:
    """Run in background"""
    return await asyncio.to_thread(blocking_function)

def on_long_operation_complete(self, result: Result) -> None:
    """Update UI with result"""
    self.update_display(result)
```

**Progress Updates:**
```python
async def ingest_with_progress(self) -> None:
    progress_bar = self.query_one("#progress", ProgressBar)
    async for progress in ingestion_progress:
        progress_bar.update(progress)
        await asyncio.sleep(0.1)  # Yield to event loop
```

---

## 11. Testing Specifications

### 11.1 Manual Test Cases

**Main Screen:**
1. Launch application → Verify welcome screen
2. Click Chat button → Verify navigation
3. Type command → Verify execution
4. Check status bar → Verify session context

**RAG Screen:**
1. Navigate to RAG → Verify empty state
2. Create repository → Verify validation
3. Select repository → Verify state display
4. Start ingestion → Verify progress bar
5. Chat with RAG → Verify message bubbles

**Chat Screen:**
1. Navigate to Chat → Verify empty history
2. Send message → Verify response
3. Stream response → Verify typing effect
4. Navigate back → Verify history preserved

### 11.2 Integration Tests

**Navigation:**
- Push/pop screen stack
- Callback execution
- State preservation

**Dependency Injection:**
- TUIProvider creates correct adapters
- Controllers receive TUI views
- Interfaces properly implemented

---

## 12. Open Questions

1. Should we support custom themes?
2. How to handle very long chat histories? (pagination vs virtual scroll)
3. Should we add mouse hover effects?
4. Support for images in chat (base64 encoding)?

---

## 13. Next Steps

1. **Design Phase:** Create component diagrams based on these specs
2. **Design Phase:** Create detailed sequence diagrams for each interaction
3. **Implementation:** Start with MainTUIScreen as proof of concept
4. **Implementation:** Add RAG screen features incrementally
5. **Testing:** Manual testing of each feature

---

*Analysis Document 003 - feature_004.modern_ui*  
*Created: 2026-06-21*  
*OMT++ Methodology v2.0*