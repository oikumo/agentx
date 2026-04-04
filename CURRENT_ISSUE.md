# Current Issue - Agent-X

> **Last Updated**: April 3, 2026

## Active Issue: Streaming Repetition Loop

### Description
When using the `chat` command in interactive streaming mode, the first response from the LLM gets stuck in a repetition loop — the same paragraph is repeated many times until truncated.

### Symptoms
- First turn: model repeats the same greeting paragraph ~6x
- Subsequent turns: model responds with generic "I am an AI language model" regardless of input
- Eventually model responds with "I'm Perplexity, a search assistant trained by Perplexity AI"

### Root Cause Analysis
1. **Provider**: `OpenRouterProvider` was configured with `model="openrouter/auto"` and `temperature=0`
2. **Auto-routing**: Routes to unknown/low-quality models that have repetition issues
3. **Temperature=0**: Deterministic output — once the model starts repeating, it loops forever
4. **Missing history**: `start_interactive_streaming()` was not adding assistant responses to history (FIXED)

### Fixes Applied
- `start_interactive_streaming()` now calls `add_assistant_message(full_response)` after streaming
- `OpenRouterProvider` updated to use `anthropic/claude-3.5-haiku` with `temperature=0.7` and `frequency_penalty=0.5`
- Added test: `test_start_interactive_streaming_adds_response_to_history`

### Status
- **Code fix**: ✅ Applied and tested (38/38 tests pass)
- **Provider fix**: ✅ Applied (Claude 3.5 Haiku with anti-repetition settings)
- **Runtime verification**: ⏳ Pending user confirmation

### Files Changed
- `agents/chat/chat_loop.py` — Added assistant response to history in streaming
- `llm_managers/providers/openrouter_provider.py` — Changed model and temperature settings
- `tests_sandbox/test_chat_loop.py` — Added regression test for history management
