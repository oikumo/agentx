# ANALYSIS 002: Dependency Inversion Architecture

**Feature:** feature_004.modern_ui  
**Date:** 2026-06-21  
**Phase:** Analysis  
**Status:** Draft

---

## 1. Overview

This analysis focuses on the dependency inversion architecture required to integrate Textual TUI while maintaining isolation from the existing UI module.

### 1.1 Problem Statement

Current architecture has controllers directly coupled to concrete View classes:
```
MainController → MainView (concrete)
RagController → RagView (concrete)
ChatController → ChatView (concrete)
```

This creates tight coupling, making it difficult to:
- Swap UI implementations
- Test controllers in isolation
- Add new UI frameworks without modifying existing code

### 1.2 Solution: Dependency Inversion

Apply SOLID Dependency Inversion Principle:
1. Controllers depend on abstractions (interfaces), not concrete implementations
2. Abstractions should not depend on details; details should depend on abstractions
3. Create adapter layer to bridge existing interfaces with TUI

---

## 2. Current State Analysis

### 2.1 Existing View Interfaces

**MainView:**
```python
class IMainViewPartner:  # ❌ Plain class, not ABC
    def run_command(self, user_input: str): pass
    def error(self): pass
    def print(self): pass
```

**Issues:**
- Not using ABC (Abstract Base Class)
- Methods are too generic
- No type hints

**ChatView:**
```python
class ChatViewPartner(ABC):  # ✅ Correct ABC
    @abstractmethod
    def process_user_message(self, user_message: str) -> bool: ...
    @abstractmethod
    def close(self) -> None: ...
```

**Issues:**
- Correctly uses ABC ✅
- Interface is minimal

**RagView:**
```python
# ❌ No interface defined
class RagView:
    controller: RagController
```

**Issues:**
- No interface at all
- Direct dependency on concrete controller

### 2.2 Current Dependency Flow

```
main.py
    └── MainController
            ├── MainView (concrete)
            └── Commands
                    └── RagCommand
                            └── RagController
                                    └── RagView (concrete)
```

**Problems:**
- High coupling
- Difficult to test
- Cannot swap UI implementations

---

## 3. Target Architecture

### 3.1 Dependency Inversion Layers

```
┌─────────────────────────────────────────────────────────┐
│                    CONTROLLER LAYER                      │
│  (Existing - Minimal Changes)                           │
│  MainController, RagController, ChatController          │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Depends on Abstraction
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   INTERFACE LAYER (NEW)                  │
│  IMainView, IRagView, IChatView (ABC interfaces)        │
│  Defined in: ui/interfaces.py                           │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Implemented By
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   ADAPTER LAYER (NEW)                    │
│  TUIAdapter, TUIRagAdapter, TUIChatAdapter              │
│  Located in: ui/tui/adapters/                           │
│  Implements interfaces using Textual widgets            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Uses
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    TUI LAYER (NEW)                       │
│  Textual-based screens and widgets                      │
│  Located in: ui/tui/screens/                            │
│  Isolated from existing ui/ module                      │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Dependency Injection

**Provider Pattern:**
```python
# providers.py
class IUIProvider(ABC):
    @abstractmethod
    def create_main_view(self, controller: IMainViewPartner) -> IMainView: ...
    @abstractmethod
    def create_rag_view(self, controller: IRagViewPartner) -> IRagView: ...
    @abstractmethod
    def create_chat_view(self, controller: IChatViewPartner) -> IChatView: ...

class TUIProvider(IUIProvider):
    def create_main_view(self, controller: IMainViewPartner) -> IMainView:
        return TUIAdapter(controller)
    # ... other methods
```

**Controller Initialization:**
```python
# Before (tight coupling):
controller = MainController()
view = MainView(controller)  # ❌ Concrete dependency

# After (dependency inversion):
provider: IUIProvider = TUIProvider()
controller = MainController()
view = provider.create_main_view(controller)  # ✅ Abstraction
```

---

## 4. Interface Definitions (Analysis)

### 4.1 IMainView Interface

**Purpose:** Abstract interface for Main Screen View

**Methods:**
- `show() -> None` - Display main screen
- `print_message(message: str) -> None` - Show info message
- `print_error_message(message: str) -> None` - Show error
- `print_warring_message(message: str) -> None` - Show warning
- `print_response(message: str) -> None` - Show response
- `print_response_error(message: str) -> None` - Show error response

**Properties:**
- `console: UIConsole` - Console reference (for backward compatibility)

### 4.2 IRagView Interface

**Purpose:** Abstract interface for RAG Screen View

**Methods:**
- `show() -> None` - Display RAG screen
- `print_message(message: str) -> None` - Show info
- `print_message_error(message: str) -> None` - Show error
- `show_repository_state(state: RagState) -> None` - Display repository info
- `show_menu() -> None` - Display menu options

**Properties:**
- `controller: RagController` - Controller reference

### 4.3 IChatView Interface

**Purpose:** Abstract interface for Chat Screen View

**Methods:**
- `show() -> None` - Display chat screen
- `show_initial_message() -> None` - Show welcome message
- `show_message(message: str) -> None` - Show message
- `show_partial_message(message: str) -> None` - Show partial (streaming)
- `show_stream_message(message: str) -> None` - Stream message
- `show_message_chat_error() -> None` - Show chat error

**Properties:**
- `controller: ChatViewPartner` - Controller reference

---

## 5. Adapter Pattern Analysis

### 5.1 TUIAdapter (Main Screen)

**Purpose:** Implement IMainView using Textual widgets

**Implementation Strategy:**
```python
class TUIAdapter(IMainView):
    def __init__(self, controller: IMainViewPartner):
        self._controller = controller
        self._app: TUIApplication | None = None
    
    def show(self) -> None:
        # Initialize Textual app
        self._app = MainTUIScreen(self._controller)
        self._app.run()
    
    def print_message(self, message: str) -> None:
        # Post message to Textual notification system
        self._app.post_message(Notification(message, type="info"))
    
    # ... other methods
```

**Key Points:**
- Implements IMainView interface
- Delegates to Textual widgets
- Maintains controller reference via interface

### 5.2 TUIRagAdapter (RAG Screen)

**Purpose:** Implement IRagView using Textual widgets

**Implementation Strategy:**
```python
class TUIRagAdapter(IRagView):
    def __init__(self, controller: IRagViewPartner):
        self._controller = controller
        self._screen: RagTUIScreen | None = None
    
    def show_repository_state(self, state: RagState) -> None:
        # Update Textual widgets with state
        if self._screen:
            self._screen.update_repository_info(state)
```

**Key Points:**
- Implements IRagView interface
- Uses Textual's reactive updates
- Real-time state display

### 5.3 TUIChatAdapter (Chat Screen)

**Purpose:** Implement IChatView using Textual widgets

**Implementation Strategy:**
```python
class TUIChatAdapter(IChatView):
    def __init__(self, controller: IChatViewPartner):
        self._controller = controller
    
    def show_stream_message(self, message: str) -> None:
        # Stream text with typing effect
        if self._screen:
            self._screen.stream_to_chat_box(message)
```

**Key Points:**
- Implements IChatView interface
- Supports streaming responses
- Message bubble display

---

## 6. Isolation Strategy

### 6.1 Module Structure

```
src/agentx/ui/
├── tui/                          # NEW - Isolated TUI module
│   ├── __init__.py
│   ├── app.py                    # TUIApplication base class
│   ├── provider.py               # TUIProvider (dependency injection)
│   ├── adapters/                 # Adapter implementations
│   │   ├── __init__.py
│   │   ├── main_adapter.py       # TUIAdapter for MainView
│   │   ├── rag_adapter.py        # TUIRagAdapter for RagView
│   │   └── chat_adapter.py       # TUIChatAdapter for ChatView
│   └── screens/                  # Textual screen implementations
│       ├── __init__.py
│       ├── main_screen.py        # MainTUIScreen
│       ├── rag_screen.py         # RagTUIScreen
│       └── chat_screen.py        # ChatTUIScreen
│
├── interfaces.py                 # NEW - ABC interfaces
│   ├── IMainView
│   ├── IRagView
│   └── IChatView
│
├── common/                       # EXISTING - Minimal changes
│   └── ui_console.py             # Keep for backward compatibility
│
└── screens/                      # EXISTING - Minimal changes
    ├── main/
    │   ├── main_controller.py    # No changes (depends on abstraction)
    │   └── main_view.py          # Minor: implement interface
    ├── rag/
    │   ├── rag_controller.py     # No changes
    │   └── rag_view.py           # Minor: implement interface
    └── chat/
        ├── chat_controller.py    # No changes
        └── chat_view.py          # Minor: implement interface
```

### 6.2 Isolation Rules

1. **TUI module (`ui/tui/`) must NOT import from:**
   - `ui/screens/` (except interfaces)
   - `ui/common/` (except for type compatibility)

2. **Existing screens (`ui/screens/`) must NOT import from:**
   - `ui/tui/` (prevents circular dependency)

3. **Interfaces (`ui/interfaces.py`) must:**
   - Use only standard library types
   - Not import from `ui/tui/` or `ui/screens/`
   - Be pure abstractions (ABC only)

4. **Controllers must:**
   - Depend on interfaces, not concrete classes
   - Receive views via dependency injection
   - Not know about TUI implementation

---

## 7. Migration Strategy

### 7.1 Phase 1: Create Infrastructure (No Breaking Changes)

1. Create `ui/interfaces.py` with ABC interfaces
2. Create `ui/tui/` module structure
3. Create `TUIProvider` class
4. Keep existing views working

### 7.2 Phase 2: Implement Adapters (Parallel to Existing)

1. Implement `TUIAdapter` for each screen
2. Implement Textual screens
3. Test adapters in isolation
4. Existing views still work

### 7.3 Phase 3: Switch to TUI (Controlled Transition)

1. Update `main.py` to use `TUIProvider`
2. Controllers now receive TUI adapters
3. Test all screens
4. Keep old views as fallback

### 7.4 Phase 4: Cleanup (Optional)

1. Remove old view implementations (if desired)
2. Keep interfaces permanent
3. Document TUI usage

---

## 8. Risk Analysis

### 8.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Textual version incompatibility | High | Pin specific version in pyproject.toml |
| Performance degradation | Medium | Profile UI updates, optimize widget tree |
| Memory leaks in Textual | Low | Monitor memory usage, proper cleanup |
| Circular dependencies | High | Enforce isolation rules, linting |

### 8.2 Architectural Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Controllers require major changes | High | Use adapter pattern, minimal interface changes |
| Existing tests break | Medium | Maintain backward compatibility during transition |
| TUI becomes tightly coupled | High | Enforce isolation via code review, linting rules |

---

## 9. Success Criteria

### 9.1 Architectural Success

- ✅ Controllers depend only on interfaces
- ✅ TUI module is completely isolated
- ✅ Existing UI module has minimal changes (<10% code change)
- ✅ Dependency injection works for all screens

### 9.2 Functional Success

- ✅ All screens (Main, Chat, RAG) work with TUI
- ✅ Session context always visible
- ✅ Consistent look and feel
- ✅ Keyboard and mouse input work

### 9.3 Quality Success

- ✅ No circular dependencies
- ✅ All interfaces use ABC
- ✅ Type hints throughout
- ✅ Clean separation of concerns

---

## 10. Next Steps

1. **Design Phase:** Create detailed component diagrams
2. **Design Phase:** Create sequence diagrams for each adapter
3. **Design Phase:** Define exact widget layouts for each screen
4. **Implementation:** Start with interfaces and provider
5. **Implementation:** Implement one adapter as proof of concept

---

*Analysis Document 002 - feature_004.modern_ui*  
*Created: 2026-06-21*  
*OMT++ Methodology v2.0*