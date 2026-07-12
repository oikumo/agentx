# Analysis 002 — ReAct Screen Dialog Diagram

**Feature:** feature_018.react_screen  
**Phase:** Analysis  
**Date:** 2026-07-11

---

## Dialog Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Main Screen                          │
│  [t] ReAct  │  🧠 ReAct button                          │
└──────────────────────┬──────────────────────────────────┘
                       │ user presses 't' or clicks button
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  ReAct Screen                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Header (clock)                                  │   │
│  ├─────────────────────────────────────────────────┤   │
│  │                                                   │   │
│  │  ┌─ Chat Area (scrollable) ──────────────────┐  │   │
│  │  │                                             │  │   │
│  │  │  🤖 ReAct Agent ready. Ask me anything!    │  │   │
│  │  │                                             │  │   │
│  │  │  You: What is 15% of 240?                  │  │   │
│  │  │                                             │  │   │
│  │  │  ┌─ 💭 Thinking ─────────────────────┐     │  │   │
│  │  │  │ The user wants 15% of 240. I      │     │  │   │
│  │  │  │ can calculate this with the       │     │  │   │
│  │  │  │ calculator tool.                   │     │  │   │
│  │  │  └───────────────────────────────────┘     │  │   │
│  │  │                                             │  │   │
│  │  │  ┌─ 🔧 Tool Call ────────────────────┐     │  │   │
│  │  │  │ calculator(expression="240*0.15") │     │  │   │
│  │  │  └───────────────────────────────────┘     │  │   │
│  │  │  ┌─ 📊 Result ───────────────────────┐     │  │   │
│  │  │  │ 36.0                               │     │  │   │
│  │  │  └───────────────────────────────────┘     │  │   │
│  │  │                                             │  │   │
│  │  │  ┌─ 💭 Thinking ─────────────────────┐     │  │   │
│  │  │  │ The calculator returned 36.0.     │     │  │   │
│  │  │  │ 15% of 240 is 36. I can now       │     │  │   │
│  │  │  │ answer the user.                   │     │  │   │
│  │  │  └───────────────────────────────────┘     │  │   │
│  │  │                                             │  │   │
│  │  │  Assistant: 15% of 240 is 36.              │  │   │
│  │  │                                             │  │   │
│  │  └─────────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  ┌─ Input ───────────────────────────────────┐   │   │
│  │  │ [Ask the ReAct agent...        ] [Ctrl+↵] │   │   │
│  │  └───────────────────────────────────────────┘   │   │
│  │                                                   │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  Footer: [q] Quit  [Esc] Back  [Ctrl+↵] Send    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## UI Elements

| Element | ID | Type | Purpose |
|---------|----|------|---------|
| Header | — | Header(show_clock) | Top bar with clock |
| Chat Area | `#react-messages` | ScrollableContainer | Scrollable message log |
| User Message | — | ChatMessage(role="user") | Right-aligned user input |
| Thinking Block | — | Static (class="thinking") | Italic reasoning display |
| Tool Call Block | — | Static (class="tool-call") | Tool name + args |
| Tool Result Block | — | Static (class="tool-result") | Tool output |
| Answer Message | — | ChatMessage(role="assistant") | Final streamed answer |
| Input | `#react-input` | Input | User question entry |
| Footer | — | Footer | Keybinding hints |

---

## Keybindings

| Key | Action | Description |
|-----|--------|-------------|
| `q` | quit | Exit application |
| `Escape` | back | Pop screen, return to Main |
| `Ctrl+Enter` | send | Submit input to agent |

---

## Visual Design Notes

- **Thinking blocks**: Dimmed/italic text with 💭 prefix, collapsible feel.
- **Tool call blocks**: Distinct background with 🔧 prefix, monospace args.
- **Tool result blocks**: Slightly different shade with 📊 prefix.
- **Answer**: Same ChatMessage style as chat screen (assistant role).
- **Streaming**: Answer text appears token-by-token (real-time).
- **Non-blocking**: UI stays responsive during agent execution (Escape works).
