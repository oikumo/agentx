# Operation Specification 001 — ReAct Screen Operations

**Feature:** feature_018.react_screen  
**Phase:** Design  
**Date:** 2026-07-11

---

## OP-1: `MainController.show_react()`

**Signature:** `def show_react(self) -> None`  
**Layer:** Controller (main_controller.py)  
**Source UC:** UC-1

**Preconditions:** Main screen is visible.  
**Postconditions:** `self._react_controller` is wired (or reused if already exists).

**Algorithm:**
```
1. IF self._react_controller IS NOT None: RETURN   # C5 idempotent
2. Create ReactController()
3. Store as self._react_controller
```

**Notes:** C5 pattern — reuse existing controller on re-entry.

---

## OP-2: `MainController.get_react_controller()`

**Signature:** `def get_react_controller(self) -> ReactController | None`  
**Layer:** Controller  

**Returns:** The wired ReactController, or None if not yet created.

---

## OP-3: `ReactTUIScreen.action_send()`

**Signature:** `def action_send(self) -> None`  
**Layer:** View  

**Preconditions:** Screen is mounted, input has text.  
**Postconditions:** User message displayed; agent invoked.

**Algorithm:**
```
1. input = query_one("#react-input", Input)
2. text = input.value.strip()
3. IF text is empty: RETURN
4. IF text.lower() in ("q", "quit", "exit"): action_quit(); RETURN
5. input.value = ""
6. show_user_message(text)
7. IF self._controller:
     self._controller.send_message(text)
```

---

## OP-4: `ReactController.send_message(user_message)`

**Signature:** `def send_message(self, user_message: str) -> bool`  
**Layer:** Controller  

**Preconditions:** Controller has a service.  
**Postconditions:** Worker thread started; returns True. Or returns False if already running.

**Algorithm:**
```
1. IF self._service.is_running: RETURN False
2. thread = Thread(target=self._run_agent, args=(user_message,), daemon=True)
3. self._worker_thread = thread
4. thread.start()
5. RETURN True
```

---

## OP-5: `ReactController._run_agent(user_message)`

**Signature:** `def _run_agent(self, user_message: str) -> None`  
**Layer:** Controller (private, runs on worker thread)  

**Algorithm:**
```
1. view = self.view  # duck-typed IReactView
2. app = self._get_app()  # stored reference to Textual App
3. def marshal(fn, *args):
       app.call_from_thread(fn, *args)
4. TRY:
     self._service.stream_agent(
       user_message=user_message,
       on_reasoning=lambda t: marshal(view.show_thinking, t),
       on_tool_call=lambda n, a: marshal(view.show_tool_call, n, a),
       on_tool_result=lambda n, r: marshal(view.show_tool_result, n, r),
       on_answer=lambda t: marshal(view.show_answer_chunk, t),
       on_done=lambda: marshal(view.show_answer_final),
       on_error=lambda e: marshal(view.show_error, str(e)),
     )
   EXCEPT Exception as e:
     marshal(view.show_error, str(e))
```

**Notes:** `app.call_from_thread` is the correct method (Screen doesn't have `call_from_thread`; only App does). The controller stores a reference to the App when the View is set or when `send_message` is called.

---

## OP-6: `ReactAgentService.stream_agent(...)`

**Signature:**
```python
def stream_agent(
    self,
    user_message: str,
    on_reasoning: Callable[[str], None],
    on_tool_call: Callable[[str, str], None],
    on_tool_result: Callable[[str, str], None],
    on_answer: Callable[[str], None],
    on_done: Callable[[], None],
    on_error: Callable[[str], None],
) -> None
```

**Layer:** Model  

**Preconditions:** Agent is created; thread_id is set.  
**Postconditions:** All events routed to callbacks; on_done or on_error called.

**Algorithm:**
```
1. self._cancel_event.clear()
2. input = {"messages": [{"role": "user", "content": user_message}]}
3. config = {"configurable": {"thread_id": self._thread_id}}
4. TRY:
     stream = self._agent.stream_events(input, config=config, version="v3")
     
     # Consume messages projection
     for message in stream.messages:
         IF self._cancel_event.is_set(): BREAK
         
         # Reasoning deltas
         for delta in message.reasoning:
             IF self._cancel_event.is_set(): BREAK
             on_reasoning(delta)
         
         # Text deltas (final answer)
         for delta in message.text:
             IF self._cancel_event.is_set(): BREAK
             on_answer(delta)
         
         # Tool calls emitted by model
         finalized = message.tool_calls.get()
         IF finalized:
             for tc in finalized:
                 on_tool_call(tc["name"], str(tc["args"]))
     
     # Consume tool_calls projection (execution lifecycle)
     for call in stream.tool_calls:
         IF self._cancel_event.is_set(): BREAK
         IF call.error:
             on_tool_result(call.tool_name, f"Error: {call.error}")
         ELSE:
             on_tool_result(call.tool_name, str(call.output))
     
     IF NOT self._cancel_event.is_set():
         on_done()
   
   EXCEPT Exception as e:
     on_error(str(e))
```

**Notes:** 
- `stream.messages` yields one `ChatModelStream` per LLM call (agent may call the model multiple times in a ReAct loop).
- `message.reasoning` is only populated if the model emits reasoning blocks (provider-dependent).
- `message.tool_calls.get()` returns finalized tool calls (non-streaming).
- `stream.tool_calls` yields tool execution events (after the model emits the call, the tool node runs).
- The cancel check is between every delta — cancel takes effect within one token.

---

## OP-7: `ReactAgentService.cancel()`

**Signature:** `def cancel(self) -> None`  
**Layer:** Model  

**Algorithm:**
```
1. self._cancel_event.set()
```

---

## OP-8: `ReactAgentService.reset_conversation()`

**Signature:** `def reset_conversation(self) -> None`  
**Layer:** Model  

**Algorithm:**
```
1. self._cancel_event.set()   # stop any in-progress run
2. self._thread_id = str(uuid7())   # new conversation
3. self._cancel_event.clear()
```

---

## OP-9: `ReactTUIScreen.show_thinking(text)`

**Signature:** `def show_thinking(self, text: str) -> None`  
**Layer:** View  

**Algorithm:**
```
1. widget = Static(f"💭 {text}", classes="react-thinking")
2. mount(widget in #react-messages)
3. scroll_to_bottom()
```

**Notes:** Each reasoning delta creates a new line. Alternatively, accumulate into a single thinking block. Design decision: accumulate into a single block per reasoning phase for cleaner display. If a new ChatModelStream starts (new reasoning phase), create a new block.

---

## OP-10: `ReactTUIScreen.show_tool_call(name, args)`

**Signature:** `def show_tool_call(self, name: str, args: str) -> None`  
**Layer:** View  

**Algorithm:**
```
1. text = f"🔧 {name}({args})"
2. widget = Static(text, classes="react-tool-call")
3. mount(widget in #react-messages)
4. scroll_to_bottom()
```

---

## OP-11: `ReactTUIScreen.show_tool_result(name, result)`

**Signature:** `def show_tool_result(self, name: str, result: str) -> None`  
**Layer:** View  

**Algorithm:**
```
1. text = f"📊 {result}"
2. widget = Static(text, classes="react-tool-result")
3. mount(widget in #react-messages)
4. scroll_to_bottom()
```

---

## OP-12: `ReactTUIScreen.show_answer_chunk(text)`

**Signature:** `def show_answer_chunk(self, text: str) -> None`  
**Layer:** View  

**Algorithm:**
```
1. IF NOT self._is_streaming:
     self._is_streaming = True
     self._streaming_text = ""
     self._streaming_widget = ChatMessage("", role="assistant")
     mount(self._streaming_widget in #react-messages)
2. self._streaming_text += text
3. self._streaming_widget.update(f"Assistant: {self._streaming_text}")
4. scroll_to_bottom()
```

---

## OP-13: `ReactTUIScreen.show_answer_final()`

**Signature:** `def show_answer_final(self) -> None`  
**Layer:** View  

**Algorithm:**
```
1. self._is_streaming = False
2. self._streaming_widget = None
3. self._streaming_text = ""
```

---

## OP-14: `ReactTUIScreen.on_unmount()`

**Signature:** `def on_unmount(self) -> None`  
**Layer:** View  

**Algorithm:**
```
1. super().on_unmount()   # cancels blocking tasks (feature_014)
2. IF self._controller and self._controller.is_running:
     self._controller.cancel()
```

---

## OP-15: `ReactAgentService.__init__()`

**Signature:**
```python
def __init__(
    self,
    llm: BaseChatModel | None = None,
    tools: list | None = None,
    system_prompt: str | None = None,
) -> None
```

**Layer:** Model  

**Algorithm:**
```
1. IF llm is None:
     llm = AIService().get_current_llm()
2. IF tools is None:
     tools = [calculator, get_current_time]   # from react_tools.py
3. IF system_prompt is None:
     system_prompt = DEFAULT_REACT_SYSTEM_PROMPT
4. self._checkpointer = InMemorySaver()
5. self._thread_id = str(uuid7())
6. self._cancel_event = threading.Event()
7. self._agent = create_agent(
     model=llm,
     tools=tools,
     system_prompt=system_prompt,
     checkpointer=self._checkpointer,
   )
```

**DEFAULT_REACT_SYSTEM_PROMPT:**
```
"You are a helpful AI assistant that uses reasoning and tools to answer "
"questions. Think step by step about what tools you need, use them when "
"necessary, and provide a clear final answer."
```
