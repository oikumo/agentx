# AgentX implementation review — confirmed defects and repair criteria

Last verified: **2026-09-19**. Status: **12 open finding groups; no application fixes applied.**

Original review revision: `f66d268d468267222946f5ba961e92b8c6f27a83` (2026-09-18).

Reverification revision: `5e62394abc4ba1054786e4b2ac9e89ce2c46f4ba`. The checkout contained unrelated harness changes. Comparing the two revisions shows no changes to `src/agentx/`, `tests/conftest.py`, `pyproject.toml`, or `uv.lock`; the application findings and source locations remain applicable. Test results below describe the working tree, not a clean checkout of that commit.

Scope: the Python application under `src/agentx/`, its console integration, and relevant tests.

The review identifies **12 confirmed finding groups: 6 P1 and 6 P2**. The P1 findings cover two filesystem sandbox escapes, ineffective policy updates, broken session creation, missing RAG chunk uploads, and prompts routed to a previously selected provider. Finding IDs are stable; related defects are grouped under the same ID rather than counted as separate findings.

All 12 groups were reproduced with **20 passing observation probes** in the accompanying [review probe module](round_001_review_probes.py). Passing means the current defect was observed; these are **not acceptance tests for repaired behavior**. The probes use disposable files, local SQLite, fake providers/retrievers, and a real local graph for the DeepAgents backend checks. No live provider requests or complete RAG conversations were exercised. The production application and `tests/` were not edited.

## Evidence and changes in this revision

- **Repeatable evidence:** The original `/tmp` probe module and logs are no longer present. Their totals are retained below as historical reports, not fresh verification. The new probe module is stored beside this report and can be rerun from the repository root.
- **AXR-03:** In addition to stale/rejected cache entries and replacement self-conflicts, an injected repository-save failure leaves a newly added rule active in memory. Transactional acceptance is therefore a reproduced requirement, not just a suggested precaution.
- **AXR-05:** Retriever construction and raised upload exceptions also escape the result error contract. A backend-only repair must address error reporting, normalized paths, and chunk identity together.
- **AXR-06:** Raised from P2 to P1 because provider selection determines where the next prompt is sent. The demonstrated request-routing mismatch can cross the user's intended local/cloud boundary; actual external disclosure was not tested.
- **Evidence limits:** “Observed” refers to the local probes. AXR-04's cached-controller analysis is a source inspection, and its restart probe requires an in-memory helper patch. AXR-05's backend checks inject the missing backend to examine downstream behavior. AXR-12 exercises only the guard. Proposed corrections and regression checks describe future work.

## Findings at a glance

Priority definitions: **P1** = address promptly because a safety/privacy boundary or core workflow fails; **P2** = a functional, recovery, or latent API defect with narrower demonstrated reach. These are repair priorities, not CVSS scores. All entries remain open.

| ID | Priority | Finding | Verification |
|---|---|---|---|
| AXR-01 | P1 | Coding edits can overwrite a file outside the sandbox through the temporary-file path | Reproduced with disposable files |
| AXR-02 | P1 | Coding search reads outside-sandbox files through symlinks | Reproduced with a disposable marker file |
| AXR-03 | P1 | Policy updates reuse stale conditions and publish state before acceptance/persistence completes | Reproduced through `add_rule_safely`, including self-conflict and injected save failure |
| AXR-04 | P1 | `new` fails with an undefined helper; fixing that alone still breaks restart recovery | Original failure reproduced; downstream behavior isolated with a runtime-only helper patch |
| AXR-05 | P1 | Default RAG tools omit the upload backend; errors and file identity also need repair | Service-created tool with mocked graph construction, plus real local `StateBackend` graph |
| AXR-06 | P1 | Changing model providers leaves the next chat request on the old provider | Reproduced through main/model controllers with fake LLMs |
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

**Boundary of the finding:** This is an application-level path-containment failure, not an escape from an operating-system container. The outside file must be writable by the AgentX process. AXR-02 similarly requires read permission. Neither probe establishes how a remote prompt alone could plant the symlink.

**Proposed correction:** Create a fresh temporary file exclusively in the validated parent directory, write through its opened handle, and atomically replace the target. Do not reuse a predictable `.tmp` name. Preserve the intended file permissions and clean up failed writes.

Exclusive temporary-file creation closes the demonstrated pre-existing-symlink attack. If other processes can rename or replace sandbox directories during an operation, path validation followed by a pathname-based write still has a race. Address that threat with directory-handle-relative operations and a defined symlink policy, or explicitly bound the sandbox guarantee to stable directory ancestry. That race was not exercised here.

**Regression check:** Pre-create the old `.tmp` symlink and verify that the outside marker is unchanged, the final target is a regular file, and the edit succeeds safely or fails explicitly.

## AXR-02 — Coding search follows symlinks outside the sandbox

**Location:** [coding_tools.py](../../src/agentx/model/coding/coding_tools.py), lines 123–138, `_file_search_impl`.

The search validates its starting directory, but each result from `rglob` is read without resolving and checking its target. `is_file()` and `read_text()` follow file symlinks. The subsequent `relative_to` check uses the lexical path of the link, so it does not detect the escape.

**Reproduction:** Place `root/link.txt` inside the configured sandbox and point it at a sibling file containing `outside-sandbox-marker`. Compare `_file_read_impl("link.txt")` with `_file_search_impl("*.txt")`.

**Observed:** Direct reading returns `Path escapes sandbox: link.txt`. Searching returns the outside marker in `FileMatch.context`, with no error.

**Impact:** The search tool can expose the first five lines of a readable outside file to the coding agent. The tool reads the entire file before constructing that preview.

**Proposed correction:** Resolve and validate every result before reading it, and read the validated target rather than the original unchecked path; alternatively, exclude symlinks from searches. Apply a consistent policy to search, read, and listing paths. As in AXR-01, a resolve-then-open sequence alone does not prove containment against concurrent directory replacement. Bound preview reads instead of loading an entire file to return five lines.

**Regression check:** Search must exclude or reject an outside symlink while still returning a regular in-sandbox file. If in-sandbox symlinks are supported, test them separately.

## AXR-03 — Policy updates retain stale conditions and mutate the cache before acceptance

**Location:** [evaluator.py](../../src/agentx/agent/model/policy/evaluator.py), `add_rule`, `add_rule_safely`, and `_compile` / `_matches` near lines 68–73, 130–146, and 189–204.

Compiled conditions are cached only by rule ID. Replacing a rule with the same ID changes `self.rules` but does not invalidate or rebuild the cached condition. Validation of a replacement also reuses that cache.

**Reproduction:** Add rule `rule-1` with condition `true` and an `EXECUTE_TOOL` action. Replace it through `add_rule_safely` with the same ID and action but condition `false`. Evaluate an empty `PolicyContext`.

**Observed:** Both additions return `True`; the stored rule says `false`; the selected action is still `EXECUTE_TOOL`. A further replacement using `@@invalid@@` is also accepted because the new expression is never compiled.

**Additional reproduced cases:**

- Submit a previously unused rule ID with condition `true` and 11 action parameters. The complexity guard rejects it, but `_compiled` retains its condition. Retry that ID with condition `false` and an otherwise valid action: the accepted rule still matches using `true` and selects `EXECUTE_TOOL`.
- Replace an existing `true` / `EXECUTE_TOOL` rule with the same ID and condition but a `PAUSE` action. `add_rule_safely` compares the old rule and replacement together, reports a conflict score of `1.0`, and rejects the replacement. A replacement must be checked against the other retained rules, not its own superseded version.
- Inject an `OSError` from `PolicyRepository.save` while adding a new rule. The exception reaches the caller, but the rule is already in `self.rules` and still selects `EXECUTE_TOOL`. The probe uses a failing repository double; it demonstrates premature in-memory publication, not a partial SQLite commit.

**Impact:** A user or reflection proposal can appear to restrict a policy while the previous permissive condition remains active. Invalid replacements bypass fail-fast validation, and a failed save can leave live behavior inconsistent with persisted state.

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

**Proposed correction:** Qualify/import the helper, then perform one coherent session transition. Prefer retaining the existing startup contract: back up the previous session and create one replacement at `current`. An explicit persisted active-session pointer is an alternative if timestamped active directories are a product requirement; startup and every session consumer must then honor it. Rebuild or rebind session-scoped controllers and repositories only after storage creation succeeds. Stop on backup failure instead of continuing with an ambiguous active session, and define rollback if replacement creation fails. Coordinate this lifecycle with AXR-08 and AXR-09.

**Regression check:** Starting from an existing current session, `new` must retain its history in the backup, accept history in the replacement, and reopen that replacement after restart. Previously opened agent screens must use the replacement's storage and sandbox. Inject backup/create failures and verify that the previous usable session remains accessible.

## AXR-05 — Default RAG search tools never upload their chunk files

**Location:** [rag_v2_tools.py](../../src/agentx/model/rag_v2/rag_v2_tools.py), lines 139–142 and 193–217; [rag_v2_agent_service.py](../../src/agentx/model/rag_v2/rag_v2_agent_service.py), tool construction near lines 104–112 and backend construction near lines 128–145.

`_search_documents_impl` uploads files only when its optional `backend` argument is supplied. `build_rag_v2_tools` binds the repository path, but its search wrapper calls the implementation without a backend. The service constructs a backend separately and never connects it to those tools.

**Reproduction:** Patch the retriever factory to return one known hit, build the actual bound tools with `build_rag_v2_tools`, and invoke `search_documents` through its public `invoke` method.

**Observed:** The result contains one hit but reports `chunks_uploaded=0` and `error=None`.

The reverification exercised the default search tool obtained from `RagV2AgentService._tools`, using a fake LLM/backend and mocked graph construction/retrieval. Even when the service receives a backend, that backend's `upload_files` is never called. This validates the service-to-tool wiring defect without claiming a complete LLM conversation was tested.

**Additional failures that a backend-only fix would expose:**

- `_search_documents_impl` counts the number of upload responses without examining each response's `error`. A backend returning `FileUploadResponse(path="chunk_0.txt", error="permission_denied")` produces `chunks_uploaded=1`, `error=None`.
- The application uploads `chunk_0.txt` as a relative key. In the installed, pinned DeepAgents `0.7.5`, filesystem middleware normalizes that read path to `/chunk_0.txt`, while `StateBackend` preserves the uploaded key exactly. A real local LangGraph probe confirmed that reading `chunk_0.txt` directly succeeds but reading the normalized `/chunk_0.txt` returns file-not-found.
- Every search starts its filenames again at `chunk_0.txt`. Two sequential searches in the same graph replaced the first chunk's contents with the second search's contents. Once upload wiring is repaired, those names cannot safely identify earlier search results for later or parallel analysis.

**Additional error-boundary failures:** Retriever construction (`build_retriever`) occurs before the retrieval `try` block, and `backend.upload_files` runs outside it. Injected exceptions in either location propagate instead of returning a `SearchDocumentsResult.error`. The factory failure is reachable through the bound public tool today; the upload failure requires injecting the missing backend. This does not establish how every graph or console caller handles those exceptions.

The local backend checks used DeepAgents' installed `backends/state.py` (`upload_files`, `read`) and `middleware/filesystem.py` (path validation before reading). `StateBackend` requires a running graph context and publishes file updates there; directly invoking a backend-bound tool outside that context is not a valid positive integration test.

**Impact:** The documented `chunk_0.txt` files are not created by retrieval. The chunk-analyst is instructed to read those files, so the retrieval → file upload → delegated analysis contract is broken. Returning hit content still permits some direct answers; this finding does not claim that every RAG question fails.

**Proposed correction:** Bind the tools to the same backend/runtime used by the service and invoke them inside the graph. Use normalized absolute backend paths with a unique retrieval identifier, such as `/retrieval/<search_id>/chunk_0.txt`, and return those exact paths with citation metadata. These are virtual backend paths, not host filesystem destinations. `RagSearchHit` currently has no backend-path field, so changing filenames alone is insufficient: the result schema, analyst instructions, and citation mapping must agree. Count only successful uploads and report per-file failures, retriever-construction failures, and raised upload exceptions explicitly. Distinguish an empty successful retrieval from an offload failure.

The recommended repair preserves the documented retrieve → offload → delegate workflow. Direct retrieval is an alternative product decision: it requires removing the file-based delegation promise and updating prompts/tests, rather than calling the current broken path repaired.

**Regression check:** Exercise the service-created search tool in a local graph and read each returned path through the analyst's actual filesystem tool. Verify sequential and parallel searches retain distinct readable files, failed uploads are not counted as successes, empty retrieval is represented correctly, and citations still map to the right chunks. Inject factory and upload exceptions as well as partial upload failures. A test that injects a permissive fake backend into the private implementation does not cover the wiring, path normalization, or graph-state contract. The current probes cover sequential overwrite; parallel search is an acceptance requirement, not an observed failure here.

## AXR-06 — Selecting a different provider leaves an existing chat on the old model

**Location:** [chat_controller.py](../../src/agentx/ui/screens/chat/chat_controller.py), lines 16 and 45; [main_controller.py](../../src/agentx/ui/screens/main/main_controller.py), lines 93–105; [models_controller.py](../../src/agentx/ui/screens/models/models_controller.py), `select_provider`.

The chat controller constructs its LLM once. Model selection updates the shared registry, but does not refresh that controller. Reopening chat returns early and reuses the previous controller and LLM.

**Reproduction:** Open chat through `MainController` using a fake OpenRouter LLM. Select Ollama through `ModelsController`, then reopen chat.

**Observed:** `selected='ollama'`, while `chat.llm.name='openrouter'`. The probe sent the next message and confirmed that only the fake OpenRouter LLM received it. Calling `_format_chat_error` for that stale LLM nevertheless labels the error as Ollama because the formatter consults the newly selected registry entry.

**Impact:** The selected-provider UI and the actual provider receiving future prompts can disagree for the rest of the process. Selecting a local provider does not necessarily move an existing conversation off its earlier cloud provider. The reproduction used fake LLMs and sent no external requests.

**Proposed correction:** Resolve or refresh the LLM when the selected provider changes, with an explicit policy for preserving conversation history. Bind each request to a model and its provider identity; use that identity in error messages. A request already running may finish with its captured provider, but the next request must honor the new selection. If creating the selected provider fails, surface that failure instead of silently continuing on the previous provider. Audit the similar cached ReAct, coding, and RAG service lifecycles; those additional modes were not demonstrated by this chat probe.

**Regression check:** Open chat with provider A, select B, reopen the existing chat, and verify that the next request reaches only B. Repeat without reopening chat. When constructing B fails, no subsequent prompt may reach A through a silent fallback. Error messages should identify the provider used or attempted for that request.

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

**Reproduction:** Open Advanced Agent with a simulated PID of 101, submit a goal, and explicitly save a snapshot successfully. Construct a fresh main controller for the same session directory with a simulated PID of 102 and open the agent with its normal `resume=True` wiring. The parameterized probe repeats this for Fast Agent.

**Observed:** The first agent is `agent_101` with one goal. The second is `agent_102` with zero goals despite the saved snapshot.

**Impact:** Saved state is not selected by the normal restart path when the PID changes. The rows and snapshot remain in the database; this is an identity/lookup failure, not demonstrated deletion. Reuse of the same controller within one process can mask the issue. Fast Agent uses the same identity pattern and reproduced the same failure. This probe does not establish automatic snapshot creation on exit.

**Proposed correction:** Persist a stable agent ID per session and agent mode. Use process/run IDs only as separate execution metadata. Define how existing `agent_<pid>` and `fast_agent_<pid>` snapshots are selected or migrated so upgrading does not strand old data. Do not choose a database-wide latest snapshot that could belong to the other mode. This repairs snapshot selection; separately verify when normal shutdown actually saves a snapshot before promising automatic restart recovery.

**Regression check:** Save with one process identity and resume with another; verify that goals, policies, and volatile snapshot memory are restored to the intended stable agent. Cover both modes in the same session database and an existing legacy-ID snapshot. Preserve saved rows during migration.

## AXR-09 — Starting a new agent session keeps the old storage and state

**Location:** [agent.py](../../src/agentx/agent/model/agent.py), lines 147–161; persistence/subsystem construction near lines 92–115.

`start_session` replaces `config` and agent IDs, but keeps the database and repository objects created by `__init__`. It also keeps the old goal tree, policy rules, memory, and reflection state. A new `persistent_path` therefore does not become the actual storage destination.

**Reproduction:** Construct an agent in directory A and submit `old-goal`. Call `start_session` with a different ID and persistent directory B, then call `persist()`.

**Observed:** `config.memory_config.persistent_path` becomes B; `agent._db.path` still points at `A/agent_session.db`; `old-goal` remains in the live tree; B contains no agent database.

**Scope:** `_register_builtin_tools(config)` does run, and the probe confirmed that the filesystem tool's sandbox root changes to B. The defect is the mixture of refreshed configuration/tools with stale repositories and session state, rather than a failure to apply every configuration field.

**Impact:** The public session API mixes old and new sessions and stores new-session data in the previous location. The reproduction used the API directly; this is distinct from the broken console `new` command in AXR-04.

**Proposed correction:** Build fresh persistence and subsystem objects from the new config, or construct a new `Agent` through the adapter. Define explicitly which runtime dependencies should carry over.

**Regression check:** Switch A → B, verify empty/new-session state, write to B only, and verify that A can still be reopened independently.

## AXR-10 — Updating a queued goal can violate the single-active-goal invariant

**Location:** [goal/manager.py](../../src/agentx/agent/model/goal/manager.py), lines 87–104.

Any transition to `COMPLETED`, `FAILED`, or `ABANDONED` promotes a pending goal. The implementation does not check whether the changed goal was active or whether another active goal remains. The `completed_id` argument to `_promote_next` is unused.

The single-active expectation comes from `GoalManager.add_goal` and the singular `active_goal()` consumer. `GoalConfig.max_active_goals` still exists with a default of 10; it does not make this accidental promotion a working concurrent scheduler. The repair should state the intended invariant and make configuration, insertion, transitions, and restoration agree.

**Reproduction:** Add goals A, B, and C. A becomes active while B and C remain pending. Set B to `ABANDONED`.

**Observed:** Both A and C are active. Repeating a terminal status update can similarly promote additional goals.

**Impact:** Scheduling and `active_goal()` no longer represent the stated single-active model. Action completion can update whichever active goal happens to appear first in the tree.

**Proposed correction:** Promote only when the active slot becomes vacant, and make repeated terminal updates idempotent. Centralize active-goal enforcement across status changes and repository loading.

**Regression check:** Completing, failing, or abandoning a pending goal must leave A as the only active goal. Completing A should promote exactly one highest-priority pending goal. Repeating a terminal update must not promote another goal; explicit activation, rollback, and repository restoration must preserve the chosen invariant.

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

**Observed:** The guard returns `True`, although the normalized destination is outside `local_sessions`. The probe also confirmed acceptance of an allowlisted symlink pointing outside and rejection of a sibling-prefix path via `PermissionError`.

**Impact:** `dangerous_delete_directory` forwards the accepted original path to `shutil.rmtree`. When `local_sessions` and the parent-traversal destination exist, that path can address an unrelated directory. Only the predicate was exercised; deletion was not invoked. Acceptance of a top-level directory symlink is not proof of deletion through it: `shutil.rmtree` normally rejects such a symlink. No application call site for this deletion helper was found in `src/agentx`, so this remains a latent API defect rather than a demonstrated console operation.

**Proposed correction:** Establish trusted allowed roots, resolve the candidate, explicitly check containment, and use the validated canonical path for deletion. Decide whether allowed roots may themselves be symlinks and whether deleting an allowed root itself is permitted. Resolving a caller-controlled root is not sufficient to establish trust, and canonicalization alone does not prevent a concurrent rename race. Apply the directory-ancestry threat model from AXR-01 consistently.

**Regression check:** Reject parent traversal, outside symlink targets, and sibling-prefix paths; accept an ordinary permitted child. Preserve or explicitly change the current rejection contract (`PermissionError`, rather than assuming a `False` return). Verify the guard independently before testing deletion with disposable directories.

## Validation and coverage gaps

**Current reproduction evidence (2026-09-19):**

```text
20 passed, 4 warnings in 4.29s
```

The [probe module](round_001_review_probes.py) is a durable review artifact outside normal `tests/` collection. Its names map to finding IDs; AXR-06 and AXR-07 share a console-wiring probe, and parameterization covers both agent modes and both RAG exception sites. Run it separately because it sets harmless import-time configuration before importing the application. It disables dotenv loading, substitutes the model-cache path, mocks external dependencies, rejects socket connections during the probes, and confines writes to pytest temporary directories. The four warnings concern dependency deprecations and SQLite's default datetime adapter.

Run from the repository root:

```bash
uv run pytest -q sandbox/consistency_enforcement/round_001_review_probes.py
# Optional: narrow the observation run to a finding, for example:
uv run pytest -q sandbox/consistency_enforcement/round_001_review_probes.py -k axr03
```

These probes intentionally assert the faulty behavior. After a repair, the corresponding observation should stop passing; replace it with a regression test that asserts the desired behavior before closing the finding. Do not add the observation module to routine CI as a correctness gate. The “Regression check” in each finding is the acceptance contract; a passing existing test suite or observation probe does not satisfy it.

**Current existing-test baseline (2026-09-19):**

| Run | Result | Scope |
|---|---|---|
| Normal full suite | **1,801 passed**, 3 warnings in 155.40s | Working-tree application and harness tests under normal collection rules |
| Explicit ReAct controller module | **16 passed** in 0.57s | Existing tests omitted by the directory-based collection hook |

Exact commands, run separately from the observation module:

```bash
env PYTHON_DOTENV_DISABLED=1 LLAMA_CPP_MODELS_CACHE_PATH=/tmp uv run pytest -q
env PYTHON_DOTENV_DISABLED=1 LLAMA_CPP_MODELS_CACHE_PATH=/tmp uv run pytest -q \
  tests/features/feature_018.react_screen/test_react_controller.py
```

The environment assignments disable dotenv loading and supply a harmless model-cache path. The full-suite warnings are dependency deprecations. These green baselines coexist with the reproduced failures because the existing tests do not cover the defective paths listed below; neither baseline establishes that the findings are repaired.

**Historical results reported on 2026-09-18:**

| Run | Reported result | Evidence available in this revision |
|---|---|---|
| Original full suite, `uv run pytest -q` | 1,739 passed, 7 warnings, 145.86s | Narrative only; the original log is absent |
| Selected application tests plus temporary probes | 534 passed, 5 warnings, 10.56s: 516 existing tests + 18 probes | Narrative only; the old probe module and log are absent |

The missing files are `/tmp/test_agentx_review_verification.py`, `/tmp/agentx-review-verification.log`, and `/tmp/agentx-implementation-review-pytest.log`. These historical totals were not independently recoverable during this revision and are not used as its verification evidence. The new 20-case module replaces that dependency for reproducing the findings.

Specific coverage gaps explain why passing tests do not resolve these defects:

- RAG's upload test injects a backend into `_search_documents_impl` directly. Its fake returns filenames, does not validate paths, and does not model upload errors or graph state. It also requires bare `chunk_0.txt` filenames, so that assertion must change with the corrected path contract. See [test_rag_v2_retrieval_tool.py](../../tests/features/feature_027.rag_v2/test_rag_v2_retrieval_tool.py).
- Tests of registries, repositories, and controllers in isolation do not establish the console lifecycle behavior described in AXR-06 through AXR-08. The regressions should exercise main-controller wiring and reopen/restart transitions.
- [tests/conftest.py](../../tests/conftest.py), lines 19–29, unconditionally ignores paths containing `react_controller` and files named `test_react_view.py`, despite the current ReAct implementation being present. Normal directory-based collection therefore omits the existing [ReAct controller test module](../../tests/features/feature_018.react_screen/test_react_controller.py). Explicit file selection is needed until the stale blanket exclusion is removed or replaced with a real availability check. This is a validation gap tracked with the repair work, not a thirteenth application finding.
- Sandbox tests need result-path and temporary-file checks in addition to direct target-path checks. Policy tests need replacement, self-conflict, failed-first-insertion, and rollback cases. Session tests must cross a process reconstruction boundary, and goal tests need terminal updates to non-active goals.

This revision verifies the reported failures, not every proposed acceptance check. Live provider compatibility, complete retrieval-to-analyst conversations, concurrent directory replacement, parallel RAG searches, automatic snapshot creation on exit, large-document embedding limits, and the studio/browser surface remain outside its demonstrated coverage.

## Repair sequence and completion criteria

| Order | Work package | Findings | Completion boundary |
|---|---|---|---|
| 1 | Filesystem containment | AXR-01, AXR-02; AXR-12 can share the path policy | Outside markers remain unchanged/unreadable through tool paths; ordinary sandbox operations still work. The latent AXR-12 repair should not delay other P1 work. |
| 2 | Provider dispatch | AXR-06 | After a selection change, the next request uses the selected provider or fails explicitly. Error attribution matches the request. |
| 3 | Policy acceptance | AXR-03 | Candidate compilation, conflict checks, persistence, and publication have one success/failure contract; rejected changes leave accepted behavior intact. |
| 4 | Session lifecycle | AXR-04, AXR-08, AXR-09 | Create, rebind, save, reconstruct, and resume agree on the active storage location and stable identity; legacy data remains recoverable. |
| 5 | RAG file handoff | AXR-05 | Service-created retrieval produces uniquely identified files readable by the actual analyst tool, with accurate errors and citations. |
| 6 | Conversation persistence and agent recovery | AXR-07, AXR-10, AXR-11 | A completed chat round survives reconstruction; goal transitions preserve the chosen active-goal limit; a failed turn does not leave later messages blocked. |

Provider refresh and conversation creation share `ChatController`; coordinate their lifecycle changes without resetting history on every reopen. AXR-04/08/09 share session ownership and should use one explicit contract. Restore ReAct collection before relying on routine suite totals for repair coverage. Independent packages can be implemented separately; no finding is closed merely because an adjacent package is complete.

For each finding, add a regression that asserts the desired public behavior, record the repaired revision and verification command/result, and change its status only after the stated acceptance checks pass. For injected downstream cases, verify the real repaired call path as well as the isolated component. Retain any untested acceptance requirement as an explicit open item.

This revision delivers the improved report and repeatable observation probes. Application changes remain proposed under the [application consistency workflow](../../.workflows/agentx/loops/consistency_enforcement.md); improving this review document does not close or implement its findings.
