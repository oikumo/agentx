# ANALYSIS 001: Modern TUI with Dependency Inversion

**Feature:** feature_004.modern_ui  
**Date:** 2026-06-21  
**Phase:** Analysis  
**Status:** Draft

---

## 1. Overview

This analysis document defines the requirements for implementing a modern Text User Interface (TUI) for AgentX using the Textual library, with strict dependency isolation and inversion principles.

### 1.1 Goal

Replace the current basic ANSI console UI with a modern TUI framework while:
- Maintaining complete isolation from existing UI module
- Using dependency inversion to decouple TUI from business logic
- Minimizing changes to existing `@src/agentx/ui/` module
- Applying to all screens (Main, Chat, RAG)
- Keeping the implementation simple

### 1.2 Key Constraints

1. **Isolated Module:** TUI implementation must be in a separate module with no direct dependencies on existing UI classes
2. **Dependency Inversion:** Existing controllers should depend on abstractions, not TUI concrete implementations
3. **Minimal Changes:** Existing UI module should require minimal to no modifications
4. **All Screens:** Main, Chat, and RAG screens must use the new TUI
5. **Simplicity:** Avoid over-engineering; use Textual's core features only

---

## 2. Use Cases

### 2.1 Primary Use Case: User Interacts with Modern TUI

**Actors:**
- User (primary)
- AgentX Application (secondary)

**Preconditions:**
- AgentX is running
- TUI module is initialized

**Main Flow:**

1. **Application Startup**
   - User launches AgentX
   - TUI module initializes the main screen
   - Modern TUI displays welcome screen with session context

2. **Main Screen Interaction**
   - TUI displays main menu with modern widgets (buttons, status bar)
   - User sees session context in status bar
   - User selects option via keyboard shortcut or mouse click
   - TUI processes input and delegates to controller

3. **Navigation to Sub-Screens**
   - User selects RAG or Chat option
   - Current screen state is saved
   - TUI transitions to sub-screen
   - Sub-screen displays with consistent look and feel

4. **RAG Screen Interaction**
   - TUI displays RAG repository status in real-time
   - User creates/selects repository via form widgets
   - User performs web ingestion with progress bar
   - User engages in chat with message bubbles

5. **Chat Screen Interaction**
   - TUI displays chat history with message bubbles
   - User types message in input field
   - TUI streams response with typing indicator
   - User exits chat, returns to parent screen

6. **Application Exit**
   - User selects quit option
   - TUI confirms exit
   - Application closes gracefully

**Postconditions:**
- User has interacted with modern TUI across all screens
- Session context is always visible
- Consistent look and feel maintained

---

### 2.2 Use Case: Display Session Context

**Preconditions:**
- Session is active
- TUI is running

**Main Flow:**

1. TUI status bar shows current session name
2. TUI status bar shows current directory
3. TUI status bar shows current screen (Main/Chat/RAG)
4. When context changes, status bar updates in real-time

**Postconditions:**
- User is always aware of session context

---

### 2.3 Use Case: Error Handling in TUI

**Preconditions:**
- Error occurs in controller or model

**Main Flow:**

1. Controller catches exception
2. Controller calls TUI error display method
3. TUI shows error in notification/toast widget
4. Error is logged
5. TUI returns to stable state

**Postconditions:**
- User is informed of error
- Application remains stable

---

## 3. Operations Extracted from Use Cases

### 3.1 TUI Lifecycle Operations

| Operation | Description | Preconditions | Postconditions |
|-----------|-------------|---------------|----------------|
| `initialize()` | Start TUI application | None | TUI running |
| `run()` | Start TUI event loop | TUI initialized | Event loop active |
| `shutdown()` | Close TUI gracefully | TUI running | TUI closed |
| `navigate_to(screen)` | Switch to different screen | TUI running | New screen active |

### 3.2 Display Operations

| Operation | Description | Preconditions | Postconditions |
|-----------|-------------|---------------|----------------|
| `show_welcome()` | Display welcome message | TUI running | Welcome shown |
| `show_menu(options)` | Display menu with options | TUI running | Menu rendered |
| `show_status(context)` | Update status bar | TUI running | Status updated |
| `show_error(message)` | Display error notification | TUI running | Error shown |
| `show_success(message)` | Display success message | TUI running | Success shown |

### 3.3 Input Operations

| Operation | Description | Preconditions | Postconditions |
|-----------|-------------|---------------|----------------|
| `capture_text(prompt)` | Get text input from user | TUI running | Text returned |
| `capture_selection(options)` | Get user selection | TUI running | Selection returned |
| `capture_confirmation(message)` | Get yes/no confirmation | TUI running | Boolean returned |

### 3.4 Advanced Display Operations

| Operation | Description | Preconditions | Postconditions |
|-----------|-------------|---------------|----------------|
| `show_progress(value, total)` | Display progress bar | TUI running | Progress shown |
| `show_table(data, columns)` | Display tabular data | TUI running | Table rendered |
| `show_message_bubble(text, type)` | Display chat message | TUI running | Message shown |
| `stream_text(text)` | Stream text with typing effect | TUI running | Text streamed |

---

## 4. Domain Concepts (Analysis Classes)

### 4.1 Core Concepts

**TUIApplication**
- Represents the main TUI application
- Manages the event loop and screen navigation
- Attributes: `current_screen`, `session_context`, `is_running`

**Screen**
- Abstract representation of a UI screen
- Attributes: `screen_id`, `title`, `widgets`
- Operations: `mount()`, `unmount()`, `update()`

**SessionContext**
- Represents current session state
- Attributes: `session_name`, `working_directory`, `current_repository`
- Operations: `update()`, `clear()`

**Widget**
- UI component (button, input, table, etc.)
- Attributes: `widget_id`, `visible`, `enabled`
- Operations: `render()`, `handle_event()`

### 4.2 Integration Concepts

**TUIAdapter**
- Bridge between existing controllers and TUI
- Implements existing view interfaces using TUI widgets
- Ensures dependency inversion

**DependencyProvider**
- Provides TUI implementations to controllers
- Manages lifecycle of TUI components
- Ensures loose coupling

---

## 5. UI Behavior Specifications

### 5.1 Screen Transitions

```
Main Screen
    ├── Show RAG Screen (push to stack)
    │       └── Return to Main (pop stack)
    └── Show Chat Screen (push to stack)
            └── Return to Main (pop stack)
```

### 5.2 Status Bar Behavior

- **Always visible** at bottom of screen
- **Left section:** Session name
- **Center section:** Current directory
- **Right section:** Current screen name
- **Updates:** Real-time on context change

### 5.3 Error Display Behavior

- **Type:** Toast notification (top-right corner)
- **Duration:** 5 seconds or until dismissed
- **Auto-dismiss:** Yes for warnings, No for critical errors
- **Logging:** All errors logged to console

### 5.4 Input Handling

- **Keyboard:** Full keyboard navigation (Tab, Enter, Esc, Arrow keys)
- **Mouse:** Click support for buttons and selections
- **Shortcuts:** Number keys for menu options, Ctrl+Q for quit

---

## 6. Integration Points

### 6.1 With Existing Controllers

**Strategy:** Adapter Pattern

```
Existing Controller → IViewPartner (interface) → TUIAdapter → Textual Widgets
```

- Existing controllers continue to call view methods
- TUIAdapter implements view interfaces using Textual
- No changes to controller logic required

### 6.2 With Session Management

**Strategy:** Observer Pattern

```
SessionController → emits context changes → TUIApplication → updates status bar
```

- TUI subscribes to session context changes
- Automatic status bar updates
- Decoupled from session management logic

### 6.3 With Model Layer

**Strategy:** Dependency Injection

```
Controller receives → ITUIProvider (abstraction)
ITUIProvider implemented by → TUIProvider (concrete)
```

- Controllers depend on abstraction
- TUIProvider implements abstraction
- Easy to swap TUI implementation

---

## 7. Requirements Summary

### 7.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR1 | Implement modern TUI using Textual library | High |
| FR2 | Apply TUI to all screens (Main, Chat, RAG) | High |
| FR3 | Display session context in status bar | High |
| FR4 | Support keyboard and mouse input | High |
| FR5 | Show progress bars for long operations | Medium |
| FR6 | Display chat messages in bubbles | Medium |
| FR7 | Show tables for repository lists | Medium |

### 7.2 Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR1 | TUI module must be isolated from existing UI | High |
| NFR2 | Use dependency inversion principle | High |
| NFR3 | Minimal changes to existing ui/ module | High |
| NFR4 | Maintain MVC++ pattern | High |
| NFR5 | Keep implementation simple | High |
| NFR6 | Consistent look and feel across screens | High |
| NFR7 | Fast response time (<100ms for UI updates) | Medium |

### 7.3 Technical Constraints

| ID | Constraint |
|----|------------|
| TC1 | Must use Textual library for TUI |
| TC2 | Must add textual to pyproject.toml dependencies |
| TC3 | TUI module must be in separate directory (e.g., `ui/tui/`) |
| TC4 | Existing UI module should have minimal changes |
| TC5 | Must maintain backward compatibility during transition |

---

## 8. Open Questions

1. Should we maintain the existing ANSI console as a fallback option?
2. How to handle screens that are not yet migrated to TUI?
3. Should TUI support theming/customization?
4. What is the minimum Textual version required?

---

## 9. Next Steps

1. **Design Phase:** Create component diagrams, interface definitions, sequence diagrams
2. **Implementation Plan:**
   - Create isolated TUI module structure
   - Implement TUIAdapter for each screen
   - Implement dependency injection providers
   - Migrate screens one by one
3. **Testing Strategy:** Manual testing of each screen, verify isolation

---

*Analysis Document 001 - feature_004.modern_ui*  
*Created: 2026-06-21*  
*OMT++ Methodology v2.0*