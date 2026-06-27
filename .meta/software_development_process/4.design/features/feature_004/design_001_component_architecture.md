# DESIGN 001: Component Architecture

**Feature:** feature_004.modern_ui  
**Date:** 2026-06-21  
**Phase:** Design  
**Status:** Draft

---

## 1. Overview

This document defines the component architecture for the modern TUI implementation with dependency inversion and isolation.

---

## 2. High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         ENTRY POINT                              │
│  main.py                                                        │
│  └── Creates Application with IUIProvider                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CONTROLLER LAYER                            │
│  (Existing - Minimal Changes)                                   │
│                                                                  │
│  MainController  ──────┬──────  RagController  ──────┬────── ChatController
│                        │                              │
│  Depends on:          │                              │
│  - IMainView          │                              │
│  - IRagView           │                              │
│  - IChatView          │                              │
└────────────────────────┼──────────────────────────────┼─────────────────────────┘
                         │                              │
                         │ Implements                   │ Implements
                         ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER (NEW)                         │
│  ui/interfaces.py                                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  IMainView      │  │  IRagView       │  │  IChatView      │ │
│  │  (ABC)          │  │  (ABC)          │  │  (ABC)          │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ +show()         │  │ +show()         │  │ +show()         │ │
│  │ +print_*()      │  │ +print_*()      │  │ +show_message() │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Implemented By
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER (NEW)                           │
│  ui/tui/adapters/                                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ TUIAdapter      │  │ TUIRagAdapter   │  │ TUIChatAdapter  │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ -controller     │  │ -controller     │  │ -controller     │ │
│  │ -app            │  │ -screen         │  │ -screen         │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ +show()         │  │ +show()         │  │ +show()         │ │
│  │ +print_*()      │  │ +show_state()   │  │ +stream_*()     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Uses
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TUI LAYER (NEW)                              │
│  ui/tui/screens/                                                │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ MainTUIScreen   │  │ RagTUIScreen    │  │ ChatTUIScreen   │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ Textual Screen  │  │ Textual Screen  │  │ Textual Screen  │ │
│  │ +widgets        │  │ +widgets        │  │ +widgets        │ │
│  │ +bindings       │  │ +bindings       │  │ +bindings       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  Common Components:                                             │
│  - SessionStatusBar (shared across screens)                     │
│  - Notification System                                          │
│  - Modal Dialogs                                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Depends On
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TEXTUAL FRAMEWORK                              │
│  (External Library - textual>=0.89.0)                           │
│  - App, Screen, Widget                                          │
│  - reactive, on_mount, on_unmount                               │
│  - Button, Input, DataTable, ProgressBar, RichLog              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Responsibilities

### 3.1 Interface Layer Components

**IUIProvider (ABC)**
```python
class IUIProvider(ABC):
    """Abstract factory for UI components"""
    
    @abstractmethod
    def create_main_view(self, controller: IMainViewPartner) -> IMainView:
        """Create main view implementation"""
        pass
    
    @abstractmethod
    def create_rag_view(self, controller: IRagViewPartner) -> IRagView:
        """Create RAG view implementation"""
        pass
    
    @abstractmethod
    def create_chat_view(self, controller: IChatViewPartner) -> IChatView:
        """Create chat view implementation"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize UI framework"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup UI resources"""
        pass
```

**IMainView (ABC)**
```python
class IMainView(ABC):
    """Abstract interface for Main Screen View"""
    
    @abstractmethod
    def show(self) -> None:
        """Display main screen"""
        pass
    
    @abstractmethod
    def print_message(self, message: str) -> None:
        """Show info message"""
        pass
    
    @abstractmethod
    def print_error_message(self, message: str) -> None:
        """Show error message"""
        pass
    
    @abstractmethod
    def print_warring_message(self, message: str) -> None:
        """Show warning message"""
        pass
    
    @abstractmethod
    def print_response(self, message: str) -> None:
        """Show response"""
        pass
    
    @abstractmethod
    def print_response_error(self, message: str) -> None:
        """Show error response"""
        pass
```

**IRagView (ABC)**
```python
class IRagView(ABC):
    """Abstract interface for RAG Screen View"""
    
    @abstractmethod
    def show(self) -> None:
        """Display RAG screen"""
        pass
    
    @abstractmethod
    def print_message(self, message: str) -> None:
        """Show info message"""
        pass
    
    @abstractmethod
    def print_message_error(self, message: str) -> None:
        """Show error message"""
        pass
    
    @abstractmethod
    def show_repository_state(self, state: RagState) -> None:
        """Display repository information"""
        pass
    
    @abstractmethod
    def show_menu(self) -> None:
        """Display menu options"""
        pass
```

**IChatView (ABC)**
```python
class IChatView(ABC):
    """Abstract interface for Chat Screen View"""
    
    @abstractmethod
    def show(self) -> None:
        """Display chat screen"""
        pass
    
    @abstractmethod
    def show_initial_message(self) -> None:
        """Show welcome message"""
        pass
    
    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show message"""
        pass
    
    @abstractmethod
    def show_partial_message(self, message: str) -> None:
        """Show partial (streaming) message"""
        pass
    
    @abstractmethod
    def show_stream_message(self, message: str) -> None:
        """Stream message with typing effect"""
        pass
    
    @abstractmethod
    def show_message_chat_error(self) -> None:
        """Show chat error"""
        pass
```

### 3.2 Adapter Layer Components

**TUIProvider**
```python
class TUIProvider(IUIProvider):
    """Concrete implementation of UI provider using Textual"""
    
    def __init__(self):
        self._app: TUIApplication | None = None
    
    def create_main_view(self, controller: IMainViewPartner) -> IMainView:
        """Create TUI adapter for main screen"""
        return TUIAdapter(controller)
    
    def create_rag_view(self, controller: IRagViewPartner) -> IRagView:
        """Create TUI adapter for RAG screen"""
        return TUIRagAdapter(controller)
    
    def create_chat_view(self, controller: IChatViewPartner) -> IChatView:
        """Create TUI adapter for chat screen"""
        return TUIChatAdapter(controller)
    
    def initialize(self) -> None:
        """Initialize Textual application"""
        self._app = TUIApplication()
    
    def shutdown(self) -> None:
        """Cleanup Textual resources"""
        if self._app:
            self._app.exit()
```

**TUIAdapter (Main Screen)**
```python
class TUIAdapter(IMainView):
    """Adapter that implements IMainView using Textual"""
    
    def __init__(self, controller: IMainViewPartner):
        self._controller = controller
        self._app: TUIApplication | None = None
    
    def show(self) -> None:
        """Initialize and run Textual main screen"""
        self._app = TUIApplication()
        self._app.push_screen(MainTUIScreen(self._controller))
        self._app.run()
    
    def print_message(self, message: str) -> None:
        """Post info notification"""
        if self._app:
            self._app.notify(message, severity="information")
    
    def print_error_message(self, message: str) -> None:
        """Post error notification"""
        if self._app:
            self._app.notify(message, severity="error", timeout=None)
    
    # ... other IMainView methods
```

**TUIRagAdapter (RAG Screen)**
```python
class TUIRagAdapter(IRagView):
    """Adapter that implements IRagView using Textual"""
    
    def __init__(self, controller: IRagViewPartner):
        self._controller = controller
        self._screen: RagTUIScreen | None = None
    
    def show(self) -> None:
        """Show RAG screen in existing TUI app"""
        # Get running app from controller
        app = self._get_app()
        app.push_screen(RagTUIScreen(self._controller))
    
    def show_repository_state(self, state: RagState) -> None:
        """Update repository state display"""
        if self._screen:
            self._screen.update_repository_info(state)
    
    # ... other IRagView methods
```

**TUIChatAdapter (Chat Screen)**
```python
class TUIChatAdapter(IChatView):
    """Adapter that implements IChatView using Textual"""
    
    def __init__(self, controller: IChatViewPartner):
        self._controller = controller
        self._screen: ChatTUIScreen | None = None
    
    def show_stream_message(self, message: str) -> None:
        """Stream message to chat display"""
        if self._screen:
            self._screen.append_to_chat(message, is_streaming=True)
    
    # ... other IChatView methods
```

### 3.3 TUI Layer Components

**TUIApplication**
```python
class TUIApplication(App):
    """Main Textual application class"""
    
    CSS_PATH = "tui.css"
    
    def on_mount(self) -> None:
        """Initialize application"""
        self.install_screen(MainTUIScreen, "main")
        self.install_screen(RagTUIScreen, "rag")
        self.install_screen(ChatTUIScreen, "chat")
        self.push_screen("main")
```

**MainTUIScreen**
```python
class MainTUIScreen(Screen):
    """Main screen with menu and command input"""
    
    # Reactive state
    session_name = reactive("default")
    working_directory = reactive("/path")
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "open_chat", "Chat"),
        Binding("r", "open_rag", "RAG"),
    ]
    
    def compose(self) -> ComposeResult:
        """Define screen layout"""
        yield Header(show_clock=True)
        yield WelcomePanel()
        yield MenuGrid()
        yield CommandInput(placeholder="(agentx) > ")
        yield SessionStatusBar()
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "btn-chat":
            self.app.push_screen(ChatTUIScreen())
        elif event.button.id == "btn-rag":
            self.app.push_screen(RagTUIScreen())
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input"""
        command = event.value
        # Delegate to controller
```

**RagTUIScreen**
```python
class RagTUIScreen(Screen):
    """RAG screen with repository management"""
    
    BINDINGS = [
        Binding("b", "go_back", "Back"),
        Binding("1", "select_repository", "Select"),
        Binding("2", "create_repository", "Create"),
        Binding("3", "web_ingestion", "Ingest"),
        Binding("4", "open_chat", "Chat"),
    ]
    
    def compose(self) -> ComposeResult:
        """Define screen layout"""
        yield Header(show_clock=True)
        yield RepositoryStatusPanel()
        yield MenuGrid()
        yield SessionStatusBar()
        yield Footer()
    
    def update_repository_info(self, state: RagState) -> None:
        """Update status panel with repository info"""
        panel = self.query_one("#status-panel", RepositoryStatusPanel)
        panel.update_state(state)
```

**ChatTUIScreen**
```python
class ChatTUIScreen(Screen):
    """Chat screen with message history"""
    
    BINDINGS = [
        Binding("b", "go_back", "Back"),
        Binding("enter", "send_message", "Send"),
    ]
    
    def compose(self) -> ComposeResult:
        """Define screen layout"""
        yield Header(show_clock=True)
        yield ChatHistory(id="chat-history")
        yield MessageInput(placeholder="Type your message...")
        yield SessionStatusBar()
        yield Footer()
    
    def append_to_chat(self, message: str, is_user: bool = False) -> None:
        """Add message to chat history"""
        history = self.query_one("#chat-history", ChatHistory)
        if is_user:
            history.add_user_message(message)
        else:
            history.add_assistant_message(message)
```

---

## 4. Data Flow Diagrams

### 4.1 Main Screen Flow

```
User Input (Keyboard/Mouse)
    │
    ▼
MainTUIScreen
    │
    ├─ Button Click ──► Navigate to sub-screen
    │
    └─ Command Input ──► Input.Submitted event
                            │
                            ▼
                        Controller.process_command()
                            │
                            ▼
                        IMainView.print_response()
                            │
                            ▼
                        TUIAdapter.print_response()
                            │
                            ▼
                        Notification widget displays result
```

### 4.2 RAG Repository Selection Flow

```
User clicks "Select Repository"
    │
    ▼
RagTUIScreen.show_repository_selection_modal()
    │
    ▼
RepositorySelectionModal mounted
    │
    ├─ Query RagProvider
    │   │
    │   ▼
    │ Repositories loaded into DataTable
    │
    └─ User clicks "Select"
            │
            ▼
        Modal closes with result
            │
            ▼
        Controller.set_repository(selected_repo)
            │
            ▼
        IRagView.show_repository_state(state)
            │
            ▼
        RepositoryStatusPanel updated
```

### 4.3 Chat Message Flow

```
User types message + Enter
    │
    ▼
ChatTUIScreen.on_input_submitted()
    │
    ▼
Controller.process_user_message(text)
    │
    ├─ Add user message to history
    │   │
    │   ▼
    │ IChatView.show_message(user_text)
    │
    └─ Call LLM (async)
            │
            ▼
        Stream response chunks
            │
            ├─ Chunk 1 ──► IChatView.show_stream_message(chunk1)
            ├─ Chunk 2 ──► IChatView.show_stream_message(chunk2)
            └─ Complete ──► IChatView.show_message(complete)
```

---

## 5. Interface Implementations

### 5.1 Existing Views → Interfaces

**MainView (Existing)**
```python
# Before: Plain class
class IMainViewPartner:
    def run_command(self, user_input: str): pass
    def error(self): pass
    def print(self): pass

# After: ABC interface
class IMainView(ABC):
    @abstractmethod
    def show(self) -> None: pass
    
    @abstractmethod
    def print_message(self, message: str) -> None: pass
    
    @abstractmethod
    def print_error_message(self, message: str) -> None: pass
    
    # ... other methods
```

**MainView Implementation (Minimal Change)**
```python
class MainView(IMainView):
    """Existing view now implements interface"""
    
    def __init__(self, controller: IMainViewPartner):
        self.controller = controller
        self.console = UIConsole("(agentx)")
    
    def show(self) -> None:
        """Existing show logic"""
        self.console.success("Agent-X")
        # ... rest of existing code
    
    def print_message(self, message: str) -> None:
        """Existing print logic"""
        self.console.info(message)
    
    # ... implement all IMainView methods
```

### 5.2 TUI Adapters → Interfaces

**TUIAdapter Implementation**
```python
class TUIAdapter(IMainView):
    """TUI implementation of IMainView"""
    
    def __init__(self, controller: IMainViewPartner):
        self._controller = controller
        self._app: TUIApplication | None = None
    
    def show(self) -> None:
        self._app = TUIApplication()
        self._app.push_screen(MainTUIScreen(self._controller))
        self._app.run()
    
    def print_message(self, message: str) -> None:
        if self._app:
            self._app.notify(message, severity="information")
    
    def print_error_message(self, message: str) -> None:
        if self._app:
            self._app.notify(message, severity="error", timeout=None)
    
    # ... implement all IMainView methods using Textual
```

---

## 6. Dependency Injection Configuration

### 6.1 Provider Registration

```python
# providers.py
class ProviderRegistry:
    """Registry for UI providers"""
    
    _providers: dict[str, IUIProvider] = {}
    
    @classmethod
    def register(cls, name: str, provider: IUIProvider) -> None:
        """Register a provider"""
        cls._providers[name] = provider
    
    @classmethod
    def get(cls, name: str) -> IUIProvider:
        """Get provider by name"""
        if name not in cls._providers:
            raise ValueError(f"Provider {name} not found")
        return cls._providers[name]

# Register providers
ProviderRegistry.register("tui", TUIProvider())
ProviderRegistry.register("console", ConsoleProvider())  # Fallback
```

### 6.2 Application Bootstrap

```python
# main.py
from agentx.ui.providers import ProviderRegistry, TUIProvider

def start():
    """Application entry point"""
    
    # Select UI provider (from config or default)
    ui_provider: IUIProvider = ProviderRegistry.get("tui")
    
    # Initialize UI
    ui_provider.initialize()
    
    # Create controllers
    session_controller = SessionController()
    main_controller = MainController(session_controller)
    
    # Create views via provider
    main_view = ui_provider.create_main_view(main_controller)
    main_controller.set_view(main_view)  # Inject view
    
    # Start application
    main_view.show()
    
    # Cleanup
    ui_provider.shutdown()
```

---

## 7. Module Structure

```
src/agentx/ui/
│
├── __init__.py
├── interfaces.py                 # NEW - ABC interfaces
│   ├── IMainView
│   ├── IRagView
│   ├── IChatView
│   └── IUIProvider
│
├── providers.py                  # NEW - Provider registry
│   ├── ProviderRegistry
│   ├── TUIProvider
│   └── ConsoleProvider (fallback)
│
├── tui/                          # NEW - Isolated TUI module
│   ├── __init__.py
│   ├── app.py                    # TUIApplication
│   ├── tui.css                   # Global styles
│   │
│   ├── adapters/                 # Adapter implementations
│   │   ├── __init__.py
│   │   ├── main_adapter.py       # TUIAdapter
│   │   ├── rag_adapter.py        # TUIRagAdapter
│   │   └── chat_adapter.py       # TUIChatAdapter
│   │
│   └── screens/                  # Textual screens
│       ├── __init__.py
│       ├── main_screen.py        # MainTUIScreen
│       ├── rag_screen.py         # RagTUIScreen
│       ├── chat_screen.py        # ChatTUIScreen
│       │
│       └── components/           # Reusable components
│           ├── __init__.py
│           ├── status_bar.py     # SessionStatusBar
│           ├── welcome_panel.py  # WelcomePanel
│           ├── menu_grid.py      # MenuGrid
│           ├── chat_history.py   # ChatHistory
│           └── repository_status.py # RepositoryStatusPanel
│
├── common/                       # EXISTING - Minimal changes
│   ├── __init__.py
│   └── ui_console.py             # Keep for backward compatibility
│
└── screens/                      # EXISTING - Implement interfaces
    ├── main/
    │   ├── main_controller.py    # No changes (depends on abstraction)
    │   └── main_view.py          # Implement IMainView
    ├── rag/
    │   ├── rag_controller.py     # No changes
    │   └── rag_view.py           # Implement IRagView
    └── chat/
        ├── chat_controller.py    # No changes
        └── chat_view.py          # Implement IChatView
```

---

## 8. CSS Styling Structure

```
src/agentx/ui/tui/
├── tui.css                       # Global theme
├── main_screen.css               # Main screen styles
├── rag_screen.css                # RAG screen styles
└── chat_screen.css               # Chat screen styles
```

**Global Theme (tui.css):**
```css
/* AgentX Theme */
Screen {
    background: $surface;
}

Header {
    background: $primary;
    color: white;
}

Footer {
    background: $surface;
    dock: bottom;
}

/* Status Bar */
SessionStatusBar {
    dock: bottom;
    background: $primary-darken-2;
    color: white;
    padding: 0 2;
}

/* Buttons */
Button {
    margin: 1;
}

Button.primary {
    background: $primary;
}

Button.success {
    background: $secondary;
}

Button.warning {
    background: $warning;
}

Button.error {
    background: $error;
}

/* Notifications */
Toast {
    background: $surface;
    border: solid $primary;
}

Toast--information {
    border-color: $primary;
}

Toast--success {
    border-color: $secondary;
}

Toast--warning {
    border-color: $warning;
}

Toast--error {
    border-color: $error;
}
```

---

## 9. Error Handling Strategy

### 9.1 Error Types

**UI Errors:**
- Widget not found → Log warning, use fallback
- Style error → Log error, continue with default style
- Navigation error → Show error notification, return to safe state

**Application Errors:**
- Controller error → Show error notification, log stack trace
- Model error → Show error notification, preserve UI state
- External service error → Show user-friendly message, retry option

### 9.2 Error Display Pattern

```python
def handle_error(self, error: Exception, context: str) -> None:
    """Standard error handling pattern"""
    
    # Log full error
    logger.error(f"{context}: {error}", exc_info=True)
    
    # Show user-friendly message
    user_message = self._get_user_message(error)
    self.notify(user_message, severity="error", timeout=None)
    
    # Return to safe state
    self.return_to_safe_state()
```

---

## 10. Performance Optimizations

### 10.1 Widget Optimization

**Use Reactive Attributes:**
```python
class RepositoryStatusPanel(Static):
    """Auto-updates when state changes"""
    
    repository_name = reactive("")
    status = reactive("unknown")
    
    def watch_repository_name(self, name: str) -> None:
        """Auto-update display"""
        self.query_one("#repo-name", Static).update(name)
```

**Batch Updates:**
```python
def update_multiple_fields(self, data: dict) -> None:
    """Batch UI updates to avoid flicker"""
    with self.batch_update():
        self.query_one("#field1").update(data["field1"])
        self.query_one("#field2").update(data["field2"])
        self.query_one("#field3").update(data["field3"])
```

### 10.2 Async Operations

**Non-blocking Pattern:**
```python
async def long_operation(self) -> Result:
    """Run in background thread"""
    return await asyncio.to_thread(blocking_function)

def on_operation_complete(self, result: Result) -> None:
    """Update UI with result"""
    self.update_display(result)
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Interface Tests:**
- Verify all interfaces are ABC
- Verify all abstract methods defined
- Verify type hints correct

**Adapter Tests:**
- Mock Textual app
- Test each adapter method
- Verify delegation to Textual widgets

### 11.2 Integration Tests

**Provider Tests:**
- TUIProvider creates correct adapters
- Adapters implement correct interfaces
- Dependency injection works

**Screen Tests:**
- Screen mounts successfully
- Widgets are created
- Bindings work

### 11.3 Manual Tests

**Screen-by-Screen:**
1. Main screen navigation
2. RAG repository operations
3. Chat message flow
4. Error handling
5. State preservation

---

## 12. Migration Checklist

### Phase 1: Infrastructure
- [ ] Create `ui/interfaces.py` with all ABC interfaces
- [ ] Create `ui/providers.py` with provider registry
- [ ] Create `ui/tui/` module structure
- [ ] Add textual to dependencies

### Phase 2: Implement Adapters
- [ ] Implement TUIAdapter (Main)
- [ ] Implement TUIRagAdapter (RAG)
- [ ] Implement TUIChatAdapter (Chat)
- [ ] Implement TUIProvider

### Phase 3: Implement Screens
- [ ] Implement MainTUIScreen
- [ ] Implement RagTUIScreen
- [ ] Implement ChatTUIScreen
- [ ] Implement common components

### Phase 4: Integration
- [ ] Update existing views to implement interfaces
- [ ] Update main.py to use TUIProvider
- [ ] Test all screens
- [ ] Document usage

### Phase 5: Cleanup (Optional)
- [ ] Remove old view implementations (if desired)
- [ ] Update documentation
- [ ] Performance profiling

---

## 13. Next Steps

1. **Implementation:** Start with interfaces and provider
2. **Implementation:** Create TUI module structure
3. **Implementation:** Implement MainTUIScreen as proof of concept
4. **Implementation:** Add RAG and Chat screens
5. **Testing:** Manual testing of each component

---

*Design Document 001 - feature_004.modern_ui*  
*Created: 2026-06-21*  
*OMT++ Methodology v2.0*