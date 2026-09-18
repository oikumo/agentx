# AgentX implementation review — errors and bugs

Reviewed and rechecked: 2026-09-18

Revision: `f66d268d468267222946f5ba961e92b8c6f27a83`

Scope: the Python application under `src/agentx/`, its console integration, and relevant tests.

The review identifies **12 confirmed finding groups: 5 high priority and 7 medium priority**. The most significant are two coding-tool sandbox escapes, stale policy conditions after updates, a broken new-session command, and missing RAG chunk uploads. Rechecking the analysis confirmed the original findings and exposed additional failure cases within AXR-03, AXR-04, and AXR-05. The corrections below expand the repair scope and distinguish observed failures from proposed regression checks.

All 12 findings were exercised again using temporary directories, temporary databases, or mocked external dependencies. The correction pass also used the installed DeepAgents `StateBackend` inside a local LangGraph execution. “Reproduced” refers to the stated local observation; live LLM providers and complete network-backed RAG conversations were not exercised. Application code and repository tests were not changed; the fixes in this document are implementation proposals.

## Corrections to the original analysis

- **AXR-03:** Cache invalidation alone is insufficient. Rejected additions can seed the cache, and replacement conflict checks compare a rule against its own previous version.
- **AXR-04:** Fixing the undefined helper exposes a second failure: the replacement uses a timestamped directory, while the next startup opens `current`. The proposed fix now covers restart recovery and cached session consumers.
- **AXR-05:** Supplying a backend alone is insufficient. Upload errors are counted as successes, chunk paths do not match the filesystem middleware's normalized paths, and repeated searches overwrite earlier chunk files.
- **AXR-06 / AXR-09 / AXR-12:** The provider probe now checks the next request and error attribution; the session analysis acknowledges that built-in tools are refreshed; deletion-guard acceptance is kept separate from evidence of actual deletion.
- **Validation:** The earlier full-suite result is historical evidence. Fresh verification is limited to AgentX application tests and disposable observation probes, with the normally excluded ReAct controller module explicitly selected.

## Findings at a glance

Priority definitions: **P1** = address promptly because a safety boundary or core workflow fails; **P2** = correct a functional defect, recovery failure, or latent unsafe API.

| ID | Priority | Finding | Verification |
|---|---|---|---|
| AXR-01 | P1 | Coding edits can overwrite a file outside the sandbox through the temporary-file path | Reproduced with disposable files |
| AXR-02 | P1 | Coding search reads outside-sandbox files through symlinks | Reproduced with a disposable marker file |
| AXR-03 | P1 | Policy updates reuse stale conditions, and rejected additions can poison later attempts | Reproduced through `add_rule_safely`, including replacement self-conflict |
| AXR-04 | P1 | `new` fails with an undefined helper; fixing that alone still breaks restart recovery | Original failure reproduced; downstream behavior isolated with a runtime-only helper patch |
| AXR-05 | P1 | RAG omits the upload backend; upload reporting and file identity also need repair | Service-created tool with mocked graph construction, plus real local `StateBackend` graph |
| AXR-06 | P2 | Changing model providers does not update an already-open chat | Reproduced through main/model controllers with fake LLMs |
| AXR-07 | P2 | The console chat entry path never starts a persisted conversation | Reproduced through main/chat controllers and real SQLite |
| AXR-08 | P2 | Process-specific agent IDs prevent saved state from resuming after restart | Reproduced with simulated PIDs and real SQLite |
| AXR-09 | P2 | `Agent.start_session` keeps the previous database and in-memory state | Reproduced with two temporary session directories |
| AXR-10 | P2 | Completing or abandoning a queued goal can create multiple active goals | Reproduced with three goals |
| AXR-11 | P2 | Tool validation errors escape the safety wrapper and leave the agent stuck | Reproduced through `AgentController.send_message` |
| AXR-12 | P2 | The directory-deletion guard accepts paths escaping its allowlist | Guard reproduced; destructive operation not invoked |

## AXR-01 — Coding edits can overwrite files outside the sandbox

**Location:** [coding_tools.py](../../src/agentx/model/coding/coding_tools.py), lines 231–234, `_file_edit_impl`.

The requested target passes `_resolve_safe_path`, but the edit is written to a predictable sibling path, `<filename>.tmp`, with `Path.write_text`. An existing symlink at that temporary path is followed without a containment check. The later `replace` moves the symlink over the original file.

**Reproduction:** Create `sandbox/file.txt` containing `old`, an outside marker file containing `outside-before`, and `sandbox/file.txt.tmp` pointing to that marker. Call `_file_edit_impl("file.txt", "old", "new")`.

**Observed:** `success=True`; the outside file now contains `new`; `sandbox/file.txt` is now a symlink. All files used for verification were disposable files under `/tmp`.

**Impact:** An ordinary edit of a valid sandbox file can overwrite a file outside that sandbox when the predictable temporary path has been prepared. This requires an existing malicious or accidental symlink; it does not require a race.

**Proposed correction:** Create a fresh temporary file exclusively in the validated parent directory, write through its opened handle, and atomically replace the target. Do not reuse a predictable `.tmp` name. Preserve the intended file permissions and clean up failed writes.

**Regression check:** Pre-create the old `.tmp` symlink and verify that the outside marker is unchanged, the final target is a regular file, and the edit succeeds safely or fails explicitly.

## AXR-02 — Coding search follows symlinks outside the sandbox

**Location:** [coding_tools.py](../../src/agentx/model/coding/coding_tools.py), lines 123–138, `_file_search_impl`.

The search validates its starting directory, but each result from `rglob` is read without resolving and checking its target. `is_file()` and `read_text()` follow file symlinks. The subsequent `relative_to` check uses the lexical path of the link, so it does not detect the escape.

**Reproduction:** Place `root/link.txt` inside the configured sandbox and point it at a sibling file containing `outside-sandbox-marker`. Compare `_file_read_impl("link.txt")` with `_file_search_impl("*.txt")`.

**Observed:** Direct reading returns `Path escapes sandbox: link.txt`. Searching returns the outside marker in `FileMatch.context`, with no error.

**Impact:** The search tool can expose the first five lines of a readable outside file to the coding agent. The tool reads the entire file before constructing that preview.

**Proposed correction:** Resolve and validate every result before reading it, or exclude symlinks from searches. Apply a consistent policy to search, read, and listing paths.

**Regression check:** Search must exclude or reject an outside symlink while still returning a regular in-sandbox file. If in-sandbox symlinks are supported, test them separately.

## AXR-03 — Policy updates retain stale conditions and mutate the cache before acceptance

**Location:** [evaluator.py](../../src/agentx/agent/model/policy/evaluator.py), `add_rule`, `add_rule_safely`, and `_compile` / `_matches` near lines 68–73, 130–146, and 189–204.

Compiled conditions are cached only by rule ID. Replacing a rule with the same ID changes `self.rules` but does not invalidate or rebuild the cached condition. Validation of a replacement also reuses that cache.

**Reproduction:** Add rule `rule-1` with condition `true` and an `EXECUTE_TOOL` action. Replace it through `add_rule_safely` with the same ID and action but condition `false`. Evaluate an empty `PolicyContext`.

**Observed:** Both additions return `True`; the stored rule says `false`; the selected action is still `EXECUTE_TOOL`. A further replacement using `@@invalid@@` is also accepted because the new expression is never compiled.

**Additional reproduced cases:**

- Submit a previously unused rule ID with condition `true` and 11 action parameters. The complexity guard rejects it, but `_compiled` retains its condition. Retry that ID with condition `false` and an otherwise valid action: the accepted rule still executes using `true`.
- Replace an existing `true` / `EXECUTE_TOOL` rule with the same ID and condition but a `PAUSE` action. `add_rule_safely` compares the old rule and replacement together, reports a conflict score of `1.0`, and rejects the replacement. A replacement must be checked against the other retained rules, not its own superseded version.

**Impact:** A user or reflection proposal can appear to restrict a policy while the previous permissive condition remains active. Invalid replacements bypass the intended fail-fast validation.

**Proposed correction:** Compile the candidate without mutating the live cache. Run conflict checks against the proposed final rule set, excluding the old version of the same ID, and apply the complexity guard before publishing anything. Persist the accepted replacement and update its rule and compiled condition together. Failed additions and replacements must leave accepted rules, compiled conditions, and persisted rules unchanged; apply the same rule to direct additions, repository reloads, and rollback.

**Regression check:** A `true` → `false` replacement must stop matching immediately; an invalid replacement must fail and leave the previous valid rule intact. A rejected first insertion must not affect a later attempt with the same ID. A legitimate action replacement must not conflict with itself, while real conflicts with other rules still fail. Verify rollback restores both the rule and its compiled expression, and persistence failures do not publish a partial update.

## AXR-04 — New-session creation fails, and a helper-only repair leaves restart recovery broken

**Location:** [session.py](../../src/agentx/model/session/session.py), `__init__`, `create_new_session`, and `backup_current_session`; [session_manager.py](../../src/agentx/model/session/session_manager.py), `create_new_session`; [commands.py](../../src/agentx/ui/screens/main/commands/commands.py), `NewSessionCommand.run`.

`Session.is_created()` calls `is_directory_exists` as an unqualified name. The module imports `utils_directories`, but never imports that function into its namespace. New-session creation calls this method while trying to back up the current session.

**Reproduction:** Construct `Session()` with `SESSION_DEFAULT_BASE_DIRECTORY` patched to a temporary directory, then call `create_new_session()`.

**Observed:** `NameError: name 'is_directory_exists' is not defined`.

**Impact:** The console `new` command catches and displays this exception, so users cannot create a new session through the normal command path. Failure occurs before the backup move.

**Downstream failure reproduced with an isolated helper patch:** Temporarily binding the missing name to `utils_directories.is_directory_exists` lets the rest of the method run. `Session()` first creates `current`; the subsequent `create(time_stamp=True)` switches the returned session to `current_<timestamp>`. A history entry written there survives on disk, but a fresh `Session()` opens the unused `current` directory and returns no history. This probe modified the module only in memory; the application still has the original `NameError`.

Static wiring review also shows that `NewSessionCommand` replaces the session manager's current session without invalidating `MainController`'s cached agent controllers. Those controllers retain the configuration and persistence objects created for the previous session. Their rebind/reset behavior must be part of the repair; the original `NameError` currently prevents reaching this transition normally.

**Proposed correction:** Qualify/import the helper, then perform one coherent session transition: back up the previous session and create a single replacement at the startup-selected location (`current`), or persist and honor an explicit active-session pointer. Rebuild or rebind session-scoped controllers and repositories after a successful transition. Define rollback when backup or replacement creation fails.

**Regression check:** Starting from an existing current session, `new` must retain its history in the backup, accept history in the replacement, and reopen that replacement after restart. Previously opened agent screens must use the replacement's storage and sandbox. Inject backup/create failures and verify that the previous usable session remains accessible.

## AXR-05 — RAG search never uploads its chunk files in the production tool path

**Location:** [rag_v2_tools.py](../../src/agentx/model/rag_v2/rag_v2_tools.py), lines 139–142 and 193–217; [rag_v2_agent_service.py](../../src/agentx/model/rag_v2/rag_v2_agent_service.py), tool construction near lines 104–112 and backend construction near lines 128–145.

`_search_documents_impl` uploads files only when its optional `backend` argument is supplied. `build_rag_v2_tools` binds the repository path, but its search wrapper calls the implementation without a backend. The service constructs a backend separately and never connects it to those tools.

**Reproduction:** Patch the retriever factory to return one known hit, build the actual bound tools with `build_rag_v2_tools`, and invoke `search_documents` through its public `invoke` method.

**Observed:** The result contains one hit but reports `chunks_uploaded=0` and `error=None`.

The correction pass exercised the default search tool obtained from `RagV2AgentService._tools`, using a fake LLM/backend and mocked graph construction/retrieval. Even when the service receives a backend, that backend's `upload_files` is never called. This validates the service-to-tool wiring defect without claiming a complete LLM conversation was tested.

**Additional failures that a backend-only fix would expose:**

- `_search_documents_impl` counts the number of upload responses without examining each response's `error`. A backend returning `FileUploadResponse(path="chunk_0.txt", error="permission_denied")` produces `chunks_uploaded=1`, `error=None`.
- The application uploads `chunk_0.txt` as a relative key. In the installed, pinned DeepAgents `0.7.5`, filesystem middleware normalizes that read path to `/chunk_0.txt`, while `StateBackend` preserves the uploaded key exactly. A real local LangGraph probe confirmed that reading `chunk_0.txt` directly succeeds but reading the normalized `/chunk_0.txt` returns file-not-found.
- Every search starts its filenames again at `chunk_0.txt`. Two sequential searches in the same graph replaced the first chunk's contents with the second search's contents. Once upload wiring is repaired, those names cannot safely identify earlier search results for later or parallel analysis.

The local backend checks used DeepAgents' installed `backends/state.py` (`upload_files`, `read`) and `middleware/filesystem.py` (path validation before reading). `StateBackend` requires a running graph context and publishes file updates there; directly invoking a backend-bound tool outside that context is not a valid positive integration test.

**Impact:** The documented `chunk_0.txt` files are not created by retrieval. The chunk-analyst is instructed to read those files, so the retrieval → file upload → delegated analysis contract is broken. Returning hit content still permits some direct answers; this finding does not claim that every RAG question fails.

**Proposed correction:** Bind the tools to the same backend/runtime used by the service and invoke them inside the graph. Use normalized absolute backend paths with a unique retrieval identifier, such as `/retrieval/<search_id>/chunk_0.txt`, and return those exact paths with citation metadata. Count only successful uploads and surface per-file failures and raised exceptions explicitly. Alternatively, deliberately use direct retrieval and remove the file-based delegation promise.

**Regression check:** Exercise the service-created search tool in a local graph and read each returned path through the analyst's actual filesystem tool. Verify two searches retain distinct readable files, failed uploads are not counted as successes, and citations still map to the right chunks. A test that injects a permissive fake backend into the private implementation does not cover the wiring, path normalization, or graph-state contract.

## AXR-06 — Selecting a different provider leaves an existing chat on the old model

**Location:** [chat_controller.py](../../src/agentx/ui/screens/chat/chat_controller.py), lines 16 and 45; [main_controller.py](../../src/agentx/ui/screens/main/main_controller.py), lines 93–105; [models_controller.py](../../src/agentx/ui/screens/models/models_controller.py), `select_provider`.

The chat controller constructs its LLM once. Model selection updates the shared registry, but does not refresh that controller. Reopening chat returns early and reuses the previous controller and LLM.

**Reproduction:** Open chat through `MainController` using a fake OpenRouter LLM. Select Ollama through `ModelsController`, then reopen chat.

**Observed:** `selected='ollama'`, while `chat.llm.name='openrouter'`. The correction pass sent the next message and confirmed that only the fake OpenRouter LLM received it. Calling `_format_chat_error` for that stale LLM nevertheless labels the error as Ollama because the formatter consults the newly selected registry entry.

**Impact:** The selected-provider UI and the actual provider receiving future prompts can disagree for the rest of the process. Selecting a local provider does not necessarily move an existing conversation off its earlier cloud provider. The reproduction used fake LLMs and sent no external requests.

**Proposed correction:** Resolve or refresh the LLM when the selected provider changes, with an explicit policy for preserving conversation history. Capture provider identity with the model used for each request so errors describe the actual provider. Audit the similar cached ReAct, coding, and RAG service lifecycles; those additional modes were not demonstrated by this chat probe.

**Regression check:** Open chat with provider A, select B, reopen the existing chat, and verify that the next request reaches only B. Error messages should identify the provider that actually handled the request.

## AXR-07 — Console chat does not start a persisted conversation

**Location:** [main_controller.py](../../src/agentx/ui/screens/main/main_controller.py), lines 93–105; [chat_view.py](../../src/agentx/ui/screens/chat/chat_view.py), lines 19–25; [chat_controller.py](../../src/agentx/ui/screens/chat/chat_controller.py), lines 18 and 56–58.

The normal console entry creates and wires a `ChatController`, then enters the view's input loop. Neither step calls `start_new_conversation`. The controller therefore retains `current_conversation_id=None`, and its conditional persistence block never runs.

**Reproduction:** Open chat through `MainController.show_chat`, backed by a temporary real `ChatHistoryRepository`, and complete one message using a fake streaming LLM.

**Observed:** Two messages exist in memory; `current_conversation_id` remains `None`; the repository has zero conversations.

**Impact:** Ordinary console chats disappear when the process exits despite the available history-persistence implementation. Tests of explicitly created conversations do not exercise this entry-path failure.

**Proposed correction:** Create a conversation on first entry or on the first accepted user message, and retain its ID while reopening the same chat. Initialize the system prompt through that same lifecycle path. Calling `ChatController.show()` alone is insufficient: it initializes in-memory history but does not create a persisted conversation either.

**Regression check:** Drive the console/main entry, send a message, reconstruct the history repository, and verify that both user and assistant messages can be retrieved.

## AXR-08 — Agent IDs derived from the PID defeat restart recovery

**Location:** [main_controller.py](../../src/agentx/ui/screens/main/main_controller.py), lines 177–186 and 220–229; [adapter.py](../../src/agentx/agent/adapter.py), lines 45–50; [agent_db.py](../../src/agentx/agent/persistence/agent_db.py), `load_latest_snapshot`.

Advanced Agent and Fast Agent receive IDs containing `os.getpid()`. Snapshot recovery looks up the latest snapshot for the new ID. A normal process restart changes that ID, even when the session directory and database are unchanged.

**Reproduction:** Open Advanced Agent with a simulated PID of 101, submit a goal, and explicitly save a snapshot successfully. Construct a fresh main controller for the same session directory with a simulated PID of 102 and open the agent with its normal `resume=True` wiring. The correction pass repeated the same probe for Fast Agent.

**Observed:** The first agent is `agent_101` with one goal. The second is `agent_102` with zero goals despite the saved snapshot.

**Impact:** Saved state is not selected by the normal restart path when the PID changes. The rows and snapshot remain in the database; this is an identity/lookup failure, not demonstrated deletion. Reuse of the same controller within one process can mask the issue. Fast Agent uses the same identity pattern and reproduced the same failure. This probe does not establish automatic snapshot creation on exit.

**Proposed correction:** Persist a stable agent ID per session and agent mode. Use process/run IDs only as separate execution metadata.

**Regression check:** Save with one process identity and resume with another; verify that goals, policies, and volatile snapshot memory are restored to the intended stable agent.

## AXR-09 — Starting a new agent session keeps the old storage and state

**Location:** [agent.py](../../src/agentx/agent/model/agent.py), lines 147–161; persistence/subsystem construction near lines 92–115.

`start_session` replaces `config` and agent IDs, but keeps the database and repository objects created by `__init__`. It also keeps the old goal tree, policy rules, memory, and reflection state. A new `persistent_path` therefore does not become the actual storage destination.

**Reproduction:** Construct an agent in directory A and submit `old-goal`. Call `start_session` with a different ID and persistent directory B, then call `persist()`.

**Observed:** `config.memory_config.persistent_path` becomes B; `agent._db.path` still points at `A/agent_session.db`; `old-goal` remains in the live tree; B contains no agent database.

**Scope correction:** `_register_builtin_tools(config)` does run, and the probe confirmed that the filesystem tool's sandbox root changes to B. The defect is the mixture of refreshed configuration/tools with stale repositories and session state, rather than a failure to apply every configuration field.

**Impact:** The public session API mixes old and new sessions and stores new-session data in the previous location. The reproduction used the API directly; this is distinct from the broken console `new` command in AXR-04.

**Proposed correction:** Build fresh persistence and subsystem objects from the new config, or construct a new `Agent` through the adapter. Define explicitly which runtime dependencies should carry over.

**Regression check:** Switch A → B, verify empty/new-session state, write to B only, and verify that A can still be reopened independently.

## AXR-10 — Updating a queued goal can violate the single-active-goal invariant

**Location:** [goal/manager.py](../../src/agentx/agent/model/goal/manager.py), lines 87–104.

Any transition to `COMPLETED`, `FAILED`, or `ABANDONED` promotes a pending goal. The implementation does not check whether the changed goal was active or whether another active goal remains. The `completed_id` argument to `_promote_next` is unused.

**Reproduction:** Add goals A, B, and C. A becomes active while B and C remain pending. Set B to `ABANDONED`.

**Observed:** Both A and C are active. Repeating a terminal status update can similarly promote additional goals.

**Impact:** Scheduling and `active_goal()` no longer represent the stated single-active model. Action completion can update whichever active goal happens to appear first in the tree.

**Proposed correction:** Promote only when the active slot becomes vacant, and make repeated terminal updates idempotent. Centralize active-goal enforcement across status changes and repository loading.

**Regression check:** Abandoning a pending goal must leave A as the only active goal. Completing A should promote exactly one highest-priority pending goal.

## AXR-11 — Validation exceptions escape safe execution and strand the agent

**Location:** [tools/registry.py](../../src/agentx/agent/model/tools/registry.py), `execute_safely`, near lines 152–164; [filesystem_tool.py](../../src/agentx/agent/model/tools/filesystem_tool.py), `validate`, near lines 92–97; [agent.py](../../src/agentx/agent/model/agent.py), `run_cycle` / `act`.

The registry calls `actuator.validate(command)` before entering its exception handler. The filesystem validator checks that `path` is truthy, but does not validate its type before using it in a `Path / path` expression. A malformed policy action can therefore raise out of the cycle. The agent has already changed state to `ACTING`, and no `finally` block restores it.

**Reproduction:** Install an otherwise valid filesystem-read policy with `path=123`, then call `AgentController.send_message`.

**Observed:** `TypeError: unsupported operand type(s) for /: 'PosixPath' and 'int'`. Afterwards, state is `ACTING`, `is_running=True`, and the next `send_message` returns `False`.

**Impact:** Bad tool arguments can crash a turn and leave subsequent messages rejected as busy. A tool validator exception violates the safe-execution contract even if the caller supplied malformed input.

**Proposed correction:** Validate argument types and include validation within the tool exception boundary. Return an unsuccessful `ActuatorResult` with an actionable validation error. Add cycle-level exception recovery so failures outside tool execution also release the busy state; preserve intentional lifecycle transitions rather than unconditionally overwriting them in a `finally` block.

**Regression check:** Exercise a wrong path type and a custom validator that raises. Each must fail safely and leave the next valid message executable.

## AXR-12 — The deletion allowlist checks unresolved paths

**Location:** [utils.py](../../src/agentx/utils/utils.py), lines 93–112 and 128–135.

The guard compares lexical `Path` objects without normalizing `..` or resolving symlinks. Its first `is_relative_to` call also discards the boolean result instead of checking it. The later `relative_to` test accepts a path such as `<cwd>/local_sessions/../unrelated` because the lexical prefix matches the allowlisted directory.

**Reproduction:** Patch the working directory to a temporary path and call `is_directory_allowed_to_deletion` with that path plus `/local_sessions/../unrelated`.

**Observed:** The guard returns `True`, although the normalized destination is outside `local_sessions`. The correction pass also confirmed acceptance of an allowlisted symlink pointing outside and rejection of a sibling-prefix path via `PermissionError`.

**Impact:** `dangerous_delete_directory` forwards the accepted original path to `shutil.rmtree`. When `local_sessions` and the parent-traversal destination exist, that path can address an unrelated directory. Only the predicate was exercised; deletion was not invoked. Acceptance of a top-level directory symlink is not proof of deletion through it: `shutil.rmtree` normally rejects such a symlink. No application call site for this deletion helper was found in `src/agentx`, so this remains a latent API defect rather than a demonstrated console operation.

**Proposed correction:** Resolve the candidate and allowed roots, explicitly check containment, and use the validated canonical path for deletion. Define whether deleting the allowlisted root itself is permitted.

**Regression check:** Reject parent traversal, outside symlink targets, and sibling-prefix paths; accept an ordinary permitted child. Preserve or explicitly change the current rejection contract (`PermissionError`, rather than assuming a `False` return). Verify the guard independently before testing deletion with disposable directories.

## Validation and coverage gaps

**Fresh application-focused verification (correction pass):**

```text
534 passed, 5 warnings in 10.56s
```

This comprises **516 existing AgentX application tests and 18 disposable observation probes**. The probes assert the faulty behavior described in this report; their passing result confirms reproduction, not that the defects have been fixed. The five warnings were dependency deprecations and the application's use of SQLite's deprecated default datetime adapter.

The exact correction-pass command, run from the repository root, was:

```bash
uv run pytest -q /tmp/test_agentx_review_verification.py \
  tests/features/feature_007.agentx_intelligent_agent_behaviour \
  tests/features/feature_013.ai_model_provider_selector \
  tests/features/feature_015.agentx_security_and_quality_hardening \
  tests/features/feature_018.react_screen/test_react_controller.py \
  tests/features/feature_019.coding_agent_screen \
  tests/features/feature_024.no_tui_full_features \
  tests/features/feature_025.coding_context_window_optimization \
  tests/features/feature_027.rag_v2 \
  tests/features/feature_029.rag_v2_slash_commands \
  tests/unit/model/test_chat_history.py
```

The `/tmp` probe module is a temporary review artifact, not a committed regression suite. It supplies harmless import-time model configuration, disables dotenv loading, and uses pytest temporary directories, real local SQLite, mocked providers/retrievers, and simulated PIDs. The RAG backend probe uses a real local graph. No live LLM, Ollama, Tavily, or remote vector-store calls were needed for the findings. The helper patch in AXR-04 exists only within its probe. No application or repository test source files were modified.

**Historical baseline (original review, not rerun for this correction pass):**

```text
uv run pytest -q
1739 passed, 7 warnings in 145.86s (0:02:25)
```

The original output remains in `/tmp/agentx-implementation-review-pytest.log`; its result was checked against that log. Temporary logs are local session evidence, not durable repository artifacts. Neither that earlier result nor the fresh selected-test result establishes correctness outside the exercised paths.

Specific coverage gaps explain why passing tests do not resolve these defects:

- RAG's upload test injects a backend into `_search_documents_impl` directly. Its fake returns filenames, does not validate paths, and does not model upload errors or graph state. That bypasses the production tool factory and backend contract responsible for AXR-05. See [test_rag_v2_retrieval_tool.py](../../tests/features/feature_027.rag_v2/test_rag_v2_retrieval_tool.py).
- Tests of registries, repositories, and controllers in isolation do not establish the console lifecycle behavior described in AXR-06 through AXR-08. The regressions should exercise main-controller wiring and reopen/restart transitions.
- [tests/conftest.py](../../tests/conftest.py), lines 19–29, unconditionally ignores paths containing `react_controller` and files named `test_react_view.py`, despite the current ReAct implementation being present. Normal directory-based collection therefore omits the existing [ReAct controller test module](../../tests/features/feature_018.react_screen/test_react_controller.py). The fresh command explicitly selects that file, and its tests pass. Remove the stale blanket exclusion or replace it with a real availability check so routine runs exercise the module too.
- Sandbox tests need result-path and temporary-file checks in addition to direct target-path checks. Policy tests need replacement, self-conflict, failed-first-insertion, and rollback cases. Session tests must cross a process reconstruction boundary, and goal tests need terminal updates to non-active goals.

This correction pass verifies the AgentX findings in this document; it is not an exhaustive application audit. Live provider compatibility, long-running concurrent streams, large-document embedding limits, and the studio/browser surface remain outside its coverage.

## Proposed correction order

1. **Contain filesystem operations:** AXR-01 and AXR-02, followed by the latent deletion guard AXR-12. These corrections are suitable for a focused safety patch with disposable-file regressions.
2. **Restore core workflows:** AXR-03, AXR-04, and AXR-05. Make policy acceptance transactional across validation/cache changes; repair session creation through restart; connect RAG retrieval to readable, uniquely named backend files with truthful upload results. Verify the complete rule-update, session-restart, and retrieval-to-analyst paths before closing these findings.
3. **Repair session and provider lifecycles:** AXR-06 through AXR-09. Establish stable agent identity, conversation creation, provider refresh, and clean session initialization together with reopen/restart tests.
4. **Harden state transitions and recovery:** AXR-10 and AXR-11, plus the stale test-collection exclusion. Verify that one failure cannot leave the application permanently busy or with multiple active goals.

These are proposed corrections, not applied fixes. This report completes the requested review artifact under the [application consistency workflow](../../.workflows/agentx/loops/consistency_enforcement.md); implementation work is a separate follow-up.
