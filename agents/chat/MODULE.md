# Agents - Chat Submodule

## Overview
Simple conversational agent implementation.

## Key Files

| File | Description |
|------|-------------|
| `simple_chat.py` | `SimpleChat` class - wraps `BaseChatModel` with a prompt template chain |

## Usage
```python
from agents.chat.simple_chat import SimpleChat
agent = SimpleChat(llm)
agent.run(query="Hello", information="")
```
