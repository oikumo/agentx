# Proposal: a mechanically managed Meta Harness sandbox

> Status: **REVISED PROPOSAL — not implemented or approved for implementation**.
> Written and reviewed again against the working implementation: 2026-10-10.
> Delivery scope: this document only. No tools, gates, manifests, projects, migration records, or other repository files are created or changed by this review.
> Evidence basis: working tree at HEAD `56e470adb4f8c830b60f4b18e8e2eef17290583f`, including pre-existing uncommitted changes. Findings describe those inspected bytes, not necessarily the committed revision. Implementation must refresh the inventory and policy baseline.

## 1. Recommended decision

Recommend **`.sandbox/` as the preferred home for new exploratory artifacts**, with explicit ownership and stable references. First compare a **convention-only pilot** with today's practice. Build an opt-in `omt_sandbox` service only if that pilot exposes failures that conventions, existing project/session tools, and Git cannot reasonably address. Neither the service nor an additional gate is yet justified by measured outcomes.

Do **not** approve the original proposal as one implementation package. It combines artifact organization, durable transactions, session permissions, an additional gate, workflow changes, and cross-system migration before demonstrating that all are needed. Split those decisions:

1. **Baseline and convention pilot.** Try one documentation activity and one pause/resume handoff using an owner, purpose, status, next action, and stable links in an ordinary document. Allocate no feature, tool, gate, runtime coordinator, or migration merely to test the idea.
2. **Conditional V1: case integrity and discovery.** If durable uncommitted snapshots or recoverable lifecycle writes solve an observed problem, implement the smallest service described below. Serialize operations within a checkout; treat branch copies as separate histories reconciled through Git. Do not build a session-lease system before a demonstrated need.
3. **Later: integrations and enforcement.** Expand adoption, add destination-specific promotion/migration, and consider an editor gate only after coverage, cost, and policy fit are demonstrated.

This preserves the lifecycle idea — **discover → create or resume → investigate → checkpoint → validate → close** — without making every conceptual step a mandatory tool call. The detailed V1 contract below is conditional design work, not permission to implement it. A directory called “sandbox” provides artifact organization; it does not confine process execution.

Keep **`.sandbox/bench/` unchanged**. It belongs to the existing net/worktree and benchmark execution plane. Neither artifact discovery nor migration may recursively treat its checkouts as case contents. Likewise, do not take ownership of the separate `.worktrees/` lane.

The current request authorizes reviewing and editing this file. It does not authorize creating a case scaffold beside it, adopting the design, implementing it, or approving any proposal referenced here. Future tools must respect equally narrow user instructions without demanding extra files or another approval just to finish already authorized document work.

### 1.1 Alternatives and decision boundary

| Option | What it adds | Cost / limitation | Decision |
|---|---|---|---|
| A — conventions + existing tools | One handoff document, stable paths, explicit owner/status, existing project links and Git history when committed. | Relies on careful handoffs; no crash-safe service transaction or automatic snapshot of uncommitted drafts. | Pilot first. If it meets the measured need, stop here. |
| B — optional artifact service | Versioned case record, selected immutable snapshots, local operation locking, recovery and validation. | Adds a maintained storage protocol, schemas, tests, and tool tokens; does not prevent external edits or solve branch merging. | Conditional V1 only for failures observed under A. |
| C — coordinated/editor-enforced lifecycle | Session ownership, broader preventive coverage, owner adapters and optional gate. | Cross-worktree consistency and host coverage become separate engineering projects. | Deferred; require an independent problem statement and cost/benefit evidence. |

Success means finding the right artifact and resuming the correct work more reliably at acceptable total cost. Folder counts, registered cases, and tool-call counts alone are not outcome measures. Existing `.projects/`, phase artifacts, and `omt_session` remain their respective authorities; the sandbox must earn its additional responsibility rather than copy them.

## 2. Evidence and deep-review findings

### 2.1 Inventory, with its denominator

The following counts were rechecked during this review. They exclude **this proposal** so they remain comparable to the initial inspection; they include regular tracked and untracked files. They exclude any reserved worktree subtree and do not follow symlinks. No symlinks or `bench/` directory were present in these two inventory roots at review time.

| Root | Files | Bytes | Immediate files / directories | Markdown / Python / JSON |
|---|---:|---:|---:|---:|
| `.sandbox/`, excluding this proposal | 152 | 1,420,410 | 54 / 10 | 119 / 12 / 13 |
| `sandbox/` | 31 | 517,039 | 3 / 3 | 30 / 1 / 0 |
| Total, excluding this proposal | 183 | 1,937,449 | — | 149 / 13 / 13 |

The other eight files are text outputs. There are 39 `.sandbox/pause_*.md` files. Including this proposal, the review-start inventory contained 184 regular files; its byte total will change as this document changes. Counts describe storage, not completed tasks, approval, or demonstrated process failures.

The ten immediate `.sandbox/` directories are `akb_smart_population_and_update`, `b2_mig_snapshot`, `feature_typesafe_jev_decision_layer`, `frontier`, `global_state`, `harness_reason`, `meta`, `proposal`, `toolbox_proposals`, and `work_contract`. The three under `sandbox/` are `consistency_enforcement`, `meta`, and `orthogonality_001_wrapper_split`. Neither sandbox root currently has a local `META.md` or `AGENTS.md`.

### 2.2 Observed problems worth solving

| Finding | Inspected evidence | Design consequence |
|---|---|---|
| Competing roots and declarations | `.workflows/META.md` says `./sandbox/` in its overview/output table and `.sandbox/` in its strategy invariants; the pause recipe writes `./sandbox/pause_*.md`. | Change current declarations and consumers together. A directory move alone does not settle policy. |
| Repeated names identify different activities | `.sandbox/meta/improvement001/` is an August harness review; `sandbox/meta/improvement001_net_enforcement/` is a September proposal. | Assign independent identities. Never merge by numeric suffix or filename recency. |
| Authored content, executable probes, and results are interleaved | `.sandbox/harness_reason/`, `global_state/`, `frontier/`, and `work_contract/` mix scripts, notes, and captured outputs. | Distinguish working files from immutable snapshots without making every note a formal experiment. |
| Resume depends on filenames and duplicated summaries | Pause files use date suffixes; `WORK.md` and project histories link directly to them. | Use explicit case/checkpoint references, with historical aliases and live-state refresh on resume. |
| Live tooling depends on exploratory paths | `reason_table.ts` resolves `.sandbox/harness_reason`; `test_probes_fixtures.py` opens `stage0_ir.json`; toolbox proposals store `draft_path` in SQLite. | Migrate each maintained consumer through its owner. Filesystem moves cannot atomically update the toolbox database. |
| Execution already has an owner | `git_worktree_root`, `worktree_lifecycle.py`, and benchmark setup use `.sandbox/bench`; worktree lifecycle also has a `.worktrees` lane. | Reserve those boundaries and discover actual worktrees through Git, not directory names alone. |
| No dedicated artifact lifecycle exists | The inspected DSL declares 11 tools and 11 gates, with no `omt_sandbox`; navigation returned no sandbox component entry. | A lifecycle tool is a candidate solution, not evidence that an additional blocking gate is necessary. |

### 2.3 Flaws in the initial design and their resolution

“Blocker” below means a blocker to shipping that part of the design, not a defect already introduced into the repository.

| Priority / flaw | Why it matters | Revised decision / verification |
|---|---|---|
| **Blocker — mandatory ceremony conflicts with the vision** | `META_VISION.md` requires zero ceremony by default and strict CI/advisory local behavior. Requiring a scaffold and several tool calls for every proposal contradicts that direction. No measured benefit was supplied. | Opt-in cases first; no new global editor gate in V1. Measure discovery/resume improvements and added calls before expanding adoption (§6, §9). |
| **Blocker — recovery and idempotency were underspecified** | The initial design blocks mutations after a partial transaction, but exposes recovery only under `migrate`. It does not define the commit point, changed-payload retries, or what survives loss of ignored state. | First-class `recover`; durable operation records; manifest replacement as the case commit point; payload-bound idempotency and explicit partial outcomes (§4.4–§5). |
| **Blocker — even a repository-common lock does not synchronize worktree copies** | A writes revision 4 and releases; B still holds revision 3 on disk, acquires the same lock, and writes a different revision 4. Both local version checks pass. A lease/generation fences writers but does not establish a common committed tip. | Narrow V1 to per-checkout operation serialization and detect divergence during Git integration. A later globally exclusive writer requires a durable shared-tip/ancestry protocol, not just leases (§4.3). |
| **Blocker — draft digests and immutable evidence were conflated** | A normal draft edit after checkpoint would invalidate a manifest digest. Conversely, matching output bytes alone does not establish which dirty source or command produced them. | Working files remain mutable; checkpoints reference immutable copies. Separate byte integrity, provenance completeness, reproducibility, and claim validity (§4.2). |
| **Blocker — tool identity was treated as an authorization mechanism** | A supplied session ID, local binding file, or `approved: true` is not proof of a user's instruction. Direct CLI writes also bypass editor hooks. | V1 stays inside case storage; every service mutation validates itself. Wider effects remain with existing owners. Promotion apply waits for an explicit host/owner authorization contract (§5, §7). |
| **High — the global ledger cannot be the sole durable audit** | `.meta/.omt/` is ignored except two compiler projections. The shared hot ledger rotates; ordinary readers use hot plus latest archive, and some append paths are best effort. | Keep immutable case operation records with the case. Mirror correlated events to the existing ledger without making it a second authority (§3, §4.4). |
| **High — existing hook coverage is incomplete** | The enforcer extracts one `filePath`/`path`/`file`. Live and dry gate loops also differ on `stop` handling. Declaring another gate does not establish multi-target or preflight parity. | Publish a tool/operation coverage matrix; demonstrate parity and unknown-target behavior before any blocking gate rollout (§6.2). |
| **High — dynamic case data would bloat compiler projections** | Putting every case summary in the tracked nav index creates budget pressure, unrelated diffs, and cross-branch contention. Checking all local cases on every harness compile couples policy compilation to untracked experiments. | Compile policy only. Use bounded on-demand lookup; defer persistent caching. Put static-contract checks in `harnessc`, artifact checks in the sandbox validator (§3, §6.3). |
| **High — V1 lacked routine correction and bounded escape paths** | Owners, titles, links, and scopes need correction; interrupted operations need repair. Without defined operations, users would edit supposedly protected metadata manually. | Constrained `update`, explicit `resume`/reopen, and `recover`; avoid session bindings in V1 and never silently rewrite sealed evidence (§5). |
| **High — universal promotion/migration exceeds one transaction boundary** | Project tooling, toolbox SQLite, files, Git worktrees, and the harness ledger do not share a transaction. A reverse path map cannot safely undo intervening edits. | Defer automatic apply; use owner-specific, resumable steps with before/after hashes, conditional compensation, and explicit partial status (§7–§8). |
| **High — old evidence could become new authority** | Imported pause notes can contain obsolete commands, approvals, and misleading “done” labels. Hashing them proves identity, not freshness or permission. | Import as historical material with unknown status where necessary; refresh live gates and never execute instructions from a checkpoint automatically (§4.2, §7). |
| **Medium — claimed costs were not measurable by current tooling** | `CEREMONY_KINDS` currently counts `q`, `think_consult`, `skip`, `tdd`, and `tdd_testlist` before the first phase. It would miss the new calls and many docs-only sessions. | Measure end-to-end calls, tokens, latency, and recovery burden separately; do not claim a zero cost from that meter (§9). |

The second review found the following remaining design flaws. These are reasoning counterexamples to the proposal, not failures reproduced against an implemented sandbox service.

| Priority / flaw | Concrete failure | Required correction |
|---|---|---|
| **Blocker — pilot came after building the costly option** | Nine operations, leases, a journal, index, ledger integration and compiler changes were required before usefulness was measured. | Pilot option A first; require an observed unmet need before option B (§1.1, §9). |
| **Blocker — retries did not bind input bytes** | `checkpoint(paths=["proposal.md"])` fails before commit; the draft changes; retrying identical JSON seals different evidence. A lost create response can also allocate a second case. | Pin a working-set digest in the request; use a caller-generated stable case ID for create retries; distinguish replaying a committed receipt from executing a new attempt (§4.4). |
| **Blocker — current-tree validation cannot establish append-only history** | Delete a closed case, or rewrite its records and recompute every hash. Validation of only surviving manifests sees no mismatch. | CI compares a trusted base tree with the proposed tree and preserves prior case IDs and sealed objects. V1 rejects divergent receipt chains and unsupported removal (§6.1). |
| **High — per-file integrity was described like a coherent snapshot** | A and B change between copies; each copied file is intact, but the pair never existed as the claimed input state. A draft also changes while close is sealing it. | Declare capture consistency, pin source hashes/inventory, recheck before publication, and distinguish an observed working set from an immutable-tree input (§4.2). |
| **High — transaction staging and durability were incomplete** | A linked worktree and its Git common directory may be on different filesystems; a rename cannot make those one atomic publication. A rename followed by failed directory flush has uncertain crash durability. | Stage published files on their destination filesystem; define the visibility point, durability acknowledgement and indeterminate outcome separately (§4.4). |
| **High — closure inventory conflicted with protected-file rules** | A requirement to hash every file under a case would read an accidentally created `.env` before rejecting it. | Classify names/types first, never read denied content, and report protected/unsafe exclusions without content hashes (§4.2). |
| **High — portability ignored Git transformations** | A clean/smudge filter or line-ending conversion changes a sealed file between local capture and a clean clone. Local hashes alone do not prove committed bytes match. | Hash and verify the staged/committed blobs for portable validation; require byte-preserving treatment of sealed data (§6.1). |
| **High — bounded results were mistaken for bounded work** | A 2 KiB response can hide an unlimited scan, oversized manifest, cyclic receipt chain or accumulating checkpoints. A stale cache misses a newly added case. | Bound admission, traversal and total storage; expose incomplete/unsupported results; defer persistent indexing until needed (§3, §4.2, §5.2). |
| **Medium — “no writes” and “complete write set” ignored runtime effects** | A rejected mutation may have created a lock; a committed mutation also writes a ledger or cache outside the case. | Separate artifact changes from declared runtime/mirror effects; never equate artifact-only scope with literally one filesystem write (§4.4, §5.2). |

### 2.4 Limits of the evidence

This review rechecked the inventory, targeted source contracts, `omt_nav`, one live net probe, and a read-only `omt_session` query bounded to 2026-10-10 UTC. That query returned 14 sessions and three displayed IDs. This establishes inspection availability, **not a cost baseline or proof that cases improve outcomes**. Session message bodies were not requested or displayed; the current `sessions` service internally normalizes selected session data, so its display limit must not be mistaken for a scan-cost bound. No sandbox scripts, migrations, or proposed feature tests were executed. Historical artifact classifications below remain migration candidates, not individually revalidated claims of completion.

The net probe reported `idle_empty`, revision 0, no pending/active/done work, four free resources, two free workers, and free verification/integration lanes. `WORK.compiled.md` remains stamped revision 60. Treat the file header as stale relative to that probe. This refactor does not repair task scheduling or infer project completion from the empty live pool.

## 3. Directory contract and ownership

This layout belongs to conditional option B. The convention-only pilot needs an ordinary handoff document, not this scaffold.

```text
.sandbox/
├── META.md                         # small policy/entry point; no live case table
├── meta_harness/
│   └── <case-id>_<slug>/
│       ├── manifest.json           # current authoritative case record
│       ├── records/                # immutable lifecycle receipts
│       ├── proposals/              # optional mutable working documents
│       ├── notes/                  # optional mutable analysis
│       ├── experiments/            # optional exploratory code/selected inputs
│       ├── evidence/               # immutable selected result bundles
│       ├── checkpoints/            # immutable handoffs and selected snapshots
│       └── .staging/               # ignored, unpublished transaction data
├── agentx/
│   └── <case-id>_<slug>/            # same contract
├── app_knowledge_base/
│   └── <case-id>_<slug>/            # same contract
├── .runs/                          # ignored disposable output, case/run scoped
└── bench/                          # reserved: existing execution owners

.meta/.omt/sandbox-runtime/         # ignored, worktree-local operation locks
```

Only the manifest and initial operation record are mandatory at creation. Optional directories appear when used. Do not create case state during a read. A separate `BRIEF.md` or materialized `CURRENT_STATE.md` is unnecessary when the purpose and progress fit in the manifest/checkpoint. `inspect` renders a compact resume view.

Resolve the actual checkout through local Git, including subdirectory invocation and linked worktrees with a `.git` file. V1 locks are local to the canonical checkout; it does **not** introduce a repository-common lease coordinator. Published temporary files must share a filesystem with their destination (§4.4). If required local locking or durable replacement is unsupported, refuse service mutations and keep inspection available.

Use `sbx_` plus a UUIDv4 as the stable ID. The caller generates it once **before** sending `create` and reuses it on retries. Allocation has no filesystem effect; the service checks syntax and exclusive creation. Under a checkout-level creation lock, reject duplicate IDs across the configured subject roots. If that census cannot complete within its bound, refuse creation instead of claiming uniqueness. Slug and subject improve readability; neither defines identity. Title changes do not rename directories; subject/path changes require a later migration.

The initial subject set is `meta_harness | agentx | app_knowledge_base`, declared once in harness configuration if adopted. Workflow headings remain human documentation, not a machine-readable registry. Cross-subject cases have one owning subject and related-subject/project references; no workflow Markdown parser is required.

| Material | Authority | Sandbox responsibility |
|---|---|---|
| Policy, declarations, budgets | `.meta/META_HARNESS.omt` | Compile static policy and adapter declarations. |
| Workflow procedure/approval boundary | Existing workflow recipe | Record its path/digest; preserve its stance without interpreting it as executable policy. |
| Accepted project design/session log | Existing project lifecycle | Link to it; do not duplicate canonical progress. |
| Feature/TDD/test completion | Existing harness mechanisms | Reference evidence without implicitly satisfying gates. |
| Work claims, execution, worktrees | Existing net/benchmark/experiment owners | Record references; never mint execution permission or duplicate their leases. |
| Current case state in a checkout | `manifest.json` | One current authority, changed through versioned operations. |
| Historical transitions/evidence | Manifest-reachable immutable records/bundles | Retain earlier outcomes; history is not independently mutable current state. |
| Operation serialization | Worktree-local OS advisory lock | Serialize cooperating service mutations of the same physical case, not Git branch copies or foreign editors. |
| Lookup/resume | Derived tool response | Read manifests on demand; no persistent case index in V1. |
| Harness-wide observability | Existing ledger | Optional correlated mirror; never the sole proof of commitment. |

Discover only direct case directories under configured subjects. Do not recursively search `bench/`, `.runs/`, `.staging/`, arbitrary legacy trees or Git-discovered checkouts. Reserved and unsupported entries are reported by name/type without opening their contents.

V1 listing uses a bounded complete census of eligible case manifests, deterministic sorting, then pagination. Recheck directory membership and read manifest digests before returning; report the observation interval and retry only within a bound if changes are detected. This is an observed catalog, not a filesystem-wide atomic snapshot. A cursor binds filters, sort order and a digest of membership plus manifest bytes; any observed change invalidates it. A cached timestamp alone is insufficient. Every page repeats the bounded census: this costs O(number of cases), which the pilot must measure. If a count/byte/time bound is reached, return `complete=false` with a narrowing action; do not issue a supposedly complete catalog cursor, global uniqueness verdict, or definitive “not found.” Direct inspection may use an explicit contained case path when a full census is unavailable.

Persistent caching is deferred until lookup measurements justify it. Any later cache must remain non-authoritative, report its observation basis, and have explicit rebuild semantics. Missing/stale caches must never hide valid cases. No dynamic case data belongs in tracked compiler projections or startup output.

“Tracked” means intended for version control, not already committed. Creating/checkpointing does not stage or commit files. Local durability survives the supported crash model; portability to another clone requires the manifest and all reachable records/snapshots to exist in the selected Git tree. Validation reports missing, ignored and untracked references separately and verifies index/commit bytes rather than inferring portability from a local filesystem check.

## 4. Case data, evidence, and lifecycle

### 4.1 Case schema

This is an **illustrative schema-shaped record**, not an allocated case or valid receipt. Placeholder references are intentionally non-evidentiary.

```json
{
  "schema_version": 1,
  "id": "sbx_21cc737b-2f42-4a9a-8c83-2d90b4bb53ed",
  "revision": 1,
  "last_record": {"path": "records/<create-record-id>.json", "sha256": "<record-digest>"},
  "title": "Sandbox lifecycle proposal",
  "subject": "meta_harness",
  "related_subjects": [],
  "owner": {"kind": "team", "ref": "meta_harness"},
  "kind": "proposal",
  "status": "active",
  "created_at": "2026-10-10T00:00:00Z",
  "updated_at": "2026-10-10T00:00:00Z",
  "purpose": "Define a sandbox artifact lifecycle and migration plan",
  "scope": {"mode": "artifact_only", "case_relative_roots": ["."], "external_effects": []},
  "links": {"workflow": null, "project": null, "features": [], "net_task": null},
  "basis": {"head": "56e470adb4f8c830b60f4b18e8e2eef17290583f", "working_tree": "dirty", "snapshot_ref": null},
  "working_artifacts": [],
  "evidence_refs": [],
  "latest_checkpoint": null,
  "closure": null,
  "disposition": null,
  "superseded_by": null
}
```

Normative rules:

- `kind` is `investigation | proposal | experiment | workflow_run`; V1 `status` is `active | paused | closed`. A later importer may add a versioned draft/adoption state. Do not ship an unused draft state or promotion field in V1.
- The durable owner is a person/team reference, separate from the session that produced a record. It supports accountability, not authentication. Null external links are valid; populated links must resolve through their owners. Never invent feature/project/task IDs to satisfy a schema.
- V1 has only `scope.mode=artifact_only`. Case-relative roots cannot name another case, checkout or absolute path. Service-owned metadata, sealed objects and staging are separately classified even when `.` is allowed. Declared runtime lock/ledger effects are internal service effects, not authority to change external product/project files.
- `revision` increases on each durable case transition. Preconditions include both that integer and SHA-256 of the exact current manifest bytes. Same revision/different bytes is stale. Do not resolve Git conflicts by choosing the larger revision.
- Use one service-owned deterministic JSON encoder: UTF-8, sorted keys, compact separators, literal Unicode, one final LF; reject duplicate keys, non-finite numbers and unsupported values on input. Schema counters are integers within the transport's exact range. Freeze cross-language transport/hash fixtures; the TypeScript adapter does not independently reserialize stored records.
- `basis.snapshot_ref=null` means dirty inputs were not captured. A HEAD hash plus `working_tree=dirty` is insufficient to reproduce a result. Workflow links carry the recipe digest where relevant. Do not serialize unrelated dirty files or the entire environment to fill fields.
- Unknown fields are rejected for the supported schema; unknown schema versions are listed as unsupported and never edited. Upgrades need an explicit plan, preserved source and validator; no upgrade during inspect/resume.
- `update` may correct title, purpose, owner, related subjects or valid links, or narrow scope with a reason. Narrowing must account for existing affected working files/references; it cannot hide them. ID, creation provenance, subject/path and prior records are immutable. External effects and scope expansion are outside V1.

### 4.2 Working artifacts, capture, and evidence

Working entries have a case-relative path and role. Their bytes may change during active drafting; they do **not** promise to match the previous checkpoint. Validation reports uncheckpointed work separately from corrupted evidence. Unregistered files are visible inventory findings, not silently trusted evidence.

A checkpoint contains progress, unresolved questions, next action, blockers, the exact case version observed, an inventory and copied immutable snapshots of explicitly selected working files. An inventory entry identifies path, file type/mode, role, disposition, size and SHA-256 where reading is permitted. Inventories exclude service-owned records/manifests/checkpoints/staging to avoid self-reference. Never recursively capture a repository just because it is linked from a note.

Classify names and file types **before** reading. Reject traversal, symlinks, hard links to managed content, devices/FIFOs/sockets, nested repositories, reserved execution roots and protected `.env` paths. Report protected/unsafe entries as exclusions with a reason and **no content hash**; do not open them for inventory, secret scanning or redaction. Intentional ordinary exclusions are recorded explicitly. A protected or unsafe entry prevents managed closure until resolved by its owner; the sandbox does not delete it automatically.

The request pins the selected path set and source hashes through a `working_set_digest`. For pause and close, that inventory covers all retained in-scope working files; the copied subset and evidence dispositions are separately explicit. Metadata-only version checks cannot detect concurrent draft edits. Copy permitted files through safely opened descriptors into unpublished objects, hash the copied bytes, and verify they match the requested source hashes. Re-enumerate/recheck the declared working set before publication; changed selection, additions, removals or bytes cause `SANDBOX_CAPTURE_CHANGED`. Do not silently reread new bytes under the same request.

Record one of these capture bases:

| Capture basis | Meaning / permitted claim |
|---|---|
| `observed_working_set` | Selected file bytes matched the requested hashes and bounded before/after checks. This detects observed changes; it does **not** prove an atomic multi-file repository snapshot against arbitrary concurrent editors. |
| `immutable_tree` | Selected inputs came from a specified immutable tree/snapshot with verified hashes. Reproducibility still depends on declared dependencies, execution conditions and available evidence. |
| `historical_unknown` | Imported or manually reported material whose original input state cannot be established. Useful history, with that limit retained. |

Cooperating writers must quiesce selected drafts during capture. A lifecycle lock serializes service operations, not external file editing. Claims that need one coherent executable input set require an immutable input tree or an independently supported snapshot mechanism. V1 does not provide a filesystem snapshot facility.

`close` records a final working inventory and checkpoint reference. Every permitted working file has an included/omitted disposition; included content is preserved in sealed objects. Closing may reuse an existing identical final checkpoint. Unselected files are explicitly excluded from the result claim, not presented as reproducible evidence. After closure, inventory drift is reported; no validator silently recomputes trusted hashes to accommodate edits. Reopen appends a new transition and releases the current closure constraint while preserving the earlier checkpoint/inventory.

Evidence bundles record:

- Observation class: `live | synthetic | mocked | historical | unexecuted`; producer, capture time, claim and limitations.
- Exact selected input/source hashes, capture basis, dirty-state limitations, file hashes and relevant dependency/tool versions.
- For executed results: redacted argv, repository-relative working directory, producer/run reference, start/end times, exit code and output references. A prose proposal gets no invented command or exit status.
- For net observations: source, revision and observation time. For transformed/redacted evidence: transformation, source reference and unavailable raw data.

Use full SHA-256 over exact bytes. A bundle manifest maps paths to hashes and is hashed separately without a self-digest cycle. A source digest alone is not a historical copy. Readers follow only objects reachable from the selected committed manifest and recheck that manifest after reading; if it changed, retry within a bound or report a concurrent update.

Return independent verdicts for **integrity**, **provenance completeness**, **reproducibility** and **claim validation**. Use `pass | fail | unknown | not_applicable` where appropriate; unexecuted or uncaptured claims cannot receive an inferred pass. Sandbox validation owns structure/integrity; result-specific validators own software/scientific claims. Neither `exit_code=0` nor self-consistent hashes proves truthful execution or user approval.

Bound storage and work, not merely response size. Proposed admission limits are 2 MiB per selected file and 20 MiB of total retained case bytes, counting reachable records, checkpoints and duplicate snapshots as well as evidence. Separately bound metadata size, file/record counts, history depth, traversal time and staging bytes. Specify numeric limits and their measured rationale before implementation. The validator rejects cycles and stops at limits with an incomplete verdict. Deduplicate immutable identical objects within a case where useful; do not introduce a cross-case object store in V1.

Quota planning must preserve a small closure/recovery allowance; nearing the limit must not force deletion of sealed evidence just to close. Admit a mutation against projected usage before publishing. Reuse an unchanged final checkpoint, or keep the case active with a clear limit error if final evidence cannot fit. Large external artifacts stay with their owning evidence system and have digest/availability references; missing external data yields `unknown` reproducibility. Durable checkpoints must not depend solely on disposable `.runs/` output.

Do not collect raw session databases, credentials or arbitrary environment dumps. Redact permitted argv/output before sealing and state replay limitations. V1 has no automatic garbage collection. A mistakenly retained sensitive artifact needs an explicitly authorized incident/removal procedure and an honest invalidation of affected evidence; “immutable” must not be used to promise that secrets can never be removed.

### 4.3 States and concurrency

| Transition | Operation | Conditions |
|---|---|---|
| New → active | `create` | Caller-supplied stable ID; valid metadata/scope; exclusive creation; initial record. |
| active → active | `update` or `checkpoint` | Expected case version; selected-source preconditions for capture. |
| active → paused | `checkpoint(pause=true)` | Committed handoff; net claims/resources are handled separately by their owner. |
| paused → active | `resume(mode=resume)` | Explicit resume, current version, fresh live-state inspection. |
| active / paused → closed | `close` | Final verified inventory/checkpoint, valid references, explicit disposition. |
| closed → active | `resume(mode=reopen)` | Explicit reason, current version and new record; preserve old closure evidence. |

Dispositions are `completed | rejected | abandoned | superseded`; a superseding case must resolve and must not create a supersession cycle. Promotion/import states are later extensions. A negative experiment or completed analysis can close without approval to implement its ideas.

Ordinary service updates and checkpoints require an active case. A paused case may close using an unchanged handoff working set; if drafts changed, resume explicitly and capture the new state. A closed case must reopen before new service-managed working content or metadata updates. Under advisory local editing, external changes remain possible and are detected, not falsely described as prevented.

Use a per-case **OS-held advisory operation lock** in the worktree-local runtime directory. Hold it from version recheck through manifest durability acknowledgement. Creation additionally uses a checkout-level namespace lock; define a fixed lock order. A crashed process releases its OS lock. Do not infer ownership from PID files, expire a live lock using wall-clock TTLs, or unlink/recreate a live lock inode. Missing/unreliable filesystem locking refuses service writes. No heartbeat, renewable session lease, one-case-per-session rule or `bind` call is needed in V1.

This protects only cooperating mutations of one physical checkout. Linked worktrees and separate clones may share a case ID and legitimately diverge. Each expected version is checked against that checkout's manifest. At integration, preserve both histories and detect divergent record ancestry; never union manifests or choose “latest timestamp/highest revision.” V1 refuses divergent integration; a user can pursue a separate related case or a later reviewed reconciliation procedure. It supplies no automatic multi-parent history merge.

A future global writer service would need a durable shared committed-tip registry, ancestry validation before accepting a checkout, handling of branch switches/removed worktrees, recovery after registry loss and a defined clone boundary. A repository-common lock or generation number alone supplies none of those. Prefer independent related cases for simultaneous investigations and leave execution/resource coordination with the existing net.

### 4.4 Transaction, retries, and recovery

Durable operations require `request_id`, stable case ID, expected version when a case exists, and a canonical request digest. Capture requests include the explicit selected inventory/`working_set_digest` as well as progress/disposition; record both the requested inputs and resulting snapshot digests. The key is scoped to that case's current reachable history in its checkout. **V1 promises no repository-wide exactly-once execution across branches, restored backups, or separate clones.**

Under the lock, search committed records before applying a stale-version check. A matching key and digest returns the original immutable receipt, with `replayed=true`, its committed version, and the separately observed current version; it does not claim that old version is still current. A changed payload returns `SANDBOX_IDEMPOTENCY_CONFLICT`. For creation, the caller reuses both its ID and request ID after a lost response; no scan of an ignored global ledger is required to recover the allocated identity. Absence of the key from a rewound/diverged history is not proof that the request never ran elsewhere.

An effect-free precondition refusal reserves no key. A partially prepared attempt with the same key must be reconciled before retry. If live input bytes no longer match a capture request, refuse that request; a refreshed request represents a new capture decision, not a silent retry.

For a supported local filesystem, the publication protocol is:

1. Validate syntax/path policy without creating a case; then acquire the operation lock and recheck expected version, reachable history and input preconditions. Session identity is audit context, not authorization or a substitute for those checks.
2. Stage snapshots and the new operation record **on the destination filesystem**, under an explicitly excluded case staging area. The record contains parent-record path/hash, prior manifest hash, contract version/policy digest, request digest, selected inputs, resulting state and artifact write set. Avoid a cycle: hash the resulting state excluding `last_record`; the manifest stores the record's path/hash. Deterministic encoding permits reconstructing the resulting full manifest. Validation checks permitted transitions and changed fields as well as hashes; a correctly hashed illegal transition is still invalid.
3. Publish immutable objects/record without overwriting existing unequal bytes. Flush their contents and required directory entries. Write/flush a new manifest in the same directory and atomically replace `manifest.json`. **Replacement is the visibility/commit point; a successful directory flush completes the durability acknowledgement.** Implementation must name its supported filesystem/platform and failure model; no universal crash guarantee is assumed.
4. Release the operation lock after durable acknowledgement. Any enabled ledger mirror is an independent observability effect with retryable, potentially duplicated delivery: readers deduplicate by case/operation/hash. The event is reconstructible from the committed receipt; pending or uncertain delivery remains visible until an authorized retry confirms it. V1 promises no background delivery daemon. Mirror failure cannot revoke the case commit. Do not rely on the current `appendLedger` void/best-effort path as evidence that a mirror persisted.
5. Return the immutable core receipt and current-attempt runtime/mirror status. A retry returns the same core receipt; mutable delivery status is not retroactively written into a sealed record.

Staging and unpublished objects may exist after failure; they are neither evidence nor committed transitions. The manifest selects the reachable chain. Temporary journals accelerate diagnosis but never become the sole commit authority. A directory without a committed manifest is an incomplete create. Readers do not adopt whichever orphan record has the highest revision.

| Observed failure point | Required result / recovery |
|---|---|
| Before artifact publication | Refuse or report failed preparation; report any staging/runtime effects. No lifecycle transition occurred. |
| Objects/record published, old manifest retained | Report uncommitted prepared objects. Recovery may finish only the exact pinned operation after revalidating state/input/authority, or leave/quarantine the orphans for a scoped cleanup. |
| Manifest replacement or durability acknowledgement uncertain | Return `recovery_required` with `commit_state=unknown` and observed before/after hashes. Do not claim either rollback or crash durability. Inspect the surviving manifest/record after recovery before retrying. |
| New manifest and objects durably acknowledged | Return committed receipt even if a later response, runtime step or ledger mirror fails. Same-key retry must not apply another transition. |
| Current files do not match either expected image | Conflict; preserve bytes, list affected paths and require reconciliation. No guessed rollback or automatic adoption. |

`recover(mode=plan|apply)` remains available when normal lifecycle operations are blocked. Planning is read-only. Apply identifies the exact request and before/after hashes, takes the same operation lock, and validates immutable objects. Completing a prepared capture requires its source preconditions still to hold, unless a separately authorized recovery explicitly accepts the already captured snapshot as historical material. Recovery never invents missing evidence, overwrites later edits, edits sealed history or widens scope.

Use outcomes `refused`, `committed`, `committed_with_warnings`, `recovery_required`; include `commit_state=not_committed | committed | unknown` for mutations. “Refused” means no persistent case-artifact changes, **not** that acquiring a runtime lock left no filesystem metadata. `changed_paths` lists artifact/staging changes; `runtime_effects` identifies lock and ledger effects outside that set, including failures. Report paths under their canonical roots without exposing their payloads. Never return an empty write set after partial publication.

No transaction covers the case, ledger, Git index and owner databases together. Service operations never stage, commit, reset or clean the repository.

## 5. Formal tool and implementation boundary

### 5.1 Thin adapter, shared service

```text
.opencode/plugins/omt_sandbox.ts
    → strict request + host/worktree context; established argvValue normalization
    → uv run --no-sync scripts/omt/sandbox_check.py <op> ...
    → scripts/omt/sandbox/  (contracts, safe paths, storage, lifecycle, validation)
    → current manifest + immutable records/snapshots + optional ledger mirror
```

This is option B, not a prerequisite for the convention pilot. The engine has no `src/agentx` dependency, network access or generic execution capability. Local plugin files are the current registration pattern; implementation also needs formal tool/navigation declarations, not an arbitrary package entry in `opencode.jsonc`.

Outer arguments are `op`, `id?`, `request?`, `expected_version?`, `request_id?`. Creation requires the caller-generated ID. `expected_version` contains revision and manifest digest; capture inputs live in the per-operation request. Reject unknown fields and invalid combinations. Bound JSON bytes, path counts, nesting and strings before expensive filesystem traversal; reject cyclic history and excessively large references during validation.

SDK-coerced JSON objects use existing `argvValue` normalization. Argument transport is literal argv, never shell interpretation. Host context identifies the canonical checkout and producer; direct CLI calls resolve the same checkout and use the same implementation. Caller-supplied session identity is an audit label, not a security credential. Missing/unsupported policy refuses mutations with a clearing action; bounded inspection can still label unsupported data.

### 5.2 Conditional V1 operations

| Operation | Contract | Writes |
|---|---|---|
| `list` | Bounded complete census, filters, catalog-pinned pagination; report incomplete scans. | None. |
| `inspect` | ID or explicit contained case path; summary, checkpoint, version, inventory and integrity warnings. Ambiguous IDs refuse. | None. |
| `create` | Stable caller-generated ID, minimal metadata, artifact-only scope, exclusive creation and initial record. | New case and declared runtime effects. |
| `update` | Allowed metadata correction or scope narrowing with reason; no moves/history edits. | Manifest/record and declared runtime effects. |
| `checkpoint` | Pinned working set, progress/next action/blockers, selected snapshots/evidence; optional pause. | Immutable objects, manifest/record and declared runtime effects. |
| `resume` | Resume paused case or explicitly reopen closed case; refresh external facts rather than replay old instructions. | Manifest/record and declared runtime effects. |
| `validate` | Local-working, portable-tree or history-delta profile; separate structure, integrity and claim verdicts. | None. |
| `close` | Final checkpoint/inventory and disposition in one request; reuse identical final evidence where possible. | Manifest/record, needed snapshots and declared runtime effects. |
| `recover` | Read-only plan or digest-pinned apply for a specific interrupted operation/mirror. | None for plan; exact reported paths/effects for apply. |

Read operations do not acquire/create locks, allocate IDs, append audit events, bind sessions, upgrade schemas or repair data. The adapter uses an already prepared environment, disables repository bytecode writes and refuses missing prerequisites instead of installing/building during a read. These guarantees cover repository artifacts and service runtime storage; any host-level logging outside that boundary must be named separately. Closed cases validate without a live producer session or runtime directory. `inspect` may return the bounded current working inventory/digest used by a subsequent capture request; a request must not silently select “whatever is there now.”

Use separate result concepts:

- An operation outcome describes whether a transition committed.
- A validation verdict describes which checks passed, failed, were not applicable or remain unknown.
- A completeness flag describes how much of the requested catalog/history was actually examined.

Thus `ok=true` for a completed read cannot be misinterpreted as “all claims passed.” No global pass is permitted when required traversal stopped at a budget limit.

Mutation responses include schema, operation, case ID, outcome/commit state, committed version, transaction ID, immutable receipt reference, artifact changes, runtime effects and warnings. Replays also identify the currently observed version. Paginate large details through a resolvable receipt reference rather than truncating the only record of effects. One effect-free rejection, detected before creating a runtime lock, is:

```json
{
  "schema_version": 1,
  "ok": false,
  "op": "checkpoint",
  "outcome": "refused",
  "commit_state": "not_committed",
  "error": {
    "code": "SANDBOX_STALE_VERSION",
    "expected_revision": 3,
    "actual_revision": 4,
    "next_action": "Inspect the current version and reconcile before retrying."
  },
  "changed_paths": [],
  "runtime_effects": []
}
```

Other stable codes include `SANDBOX_BUSY`, `SANDBOX_CLOSED`, `SANDBOX_PATH_ESCAPE`, `SANDBOX_CAPTURE_CHANGED`, `SANDBOX_EVIDENCE_CHANGED`, `SANDBOX_SCOPE_CONFLICT`, `SANDBOX_IDEMPOTENCY_CONFLICT`, `SANDBOX_SCHEMA_UNSUPPORTED`, `SANDBOX_HISTORY_CONFLICT`, `SANDBOX_RECOVERY_REQUIRED` and `SANDBOX_LIMIT_EXCEEDED`. Errors identify a bounded clearing action; no error instructs automatic destructive repair.

### 5.3 Deferred capabilities

Session binding/leases, persistent catalog caches, import, schema upgrades, automatic branch reconciliation, `promote` and `migrate` are later candidates. Their absence is explicit, not hidden behind unused fields or a nonfunctional approval adapter. V1 may produce ordinary human-reviewable plans; execution stays with the authorized destination owner.

No generic `run`, `exec`, recursive cleanup, sealed-object deletion or network fetch belongs in this service. The current `omt_session` adapter refuses `experiment(sub=run)` with `no_safe_launch`; a case does not make an experiment launcher available. Capture results only from an independently available, authorized execution path.

## 6. Enforcement and integration

### 6.1 Policy fit and adoption modes

Separate **data integrity** from **mandatory workflow participation**:

| Boundary | V1 behavior | Later expansion condition |
|---|---|---|
| Lifecycle service/CLI writes | Enforce schema, local operation locking, paths, immutable-object rules and transaction preconditions. | Required if the service is built. |
| Local ordinary document edits | Advisory case discovery/checkpoint guidance. Existing user scope and harness gates remain in force. | Scoped opt-in editor enforcement only after coverage canaries and pilot results. |
| Harness CI for committed managed cases | Strict portable-tree validation plus a base-to-proposed-tree history comparison. | No ephemeral session binding or private session database dependency. |
| Unmanaged legacy artifacts | Readable and editable under current owners/rules; report migration debt. | No abrupt whole-tree deny. Adopt a reviewed ownership group at a time. |
| Product without the harness | No sandbox service requirement for build/test/runtime. | Preserve the existing split-proof obligations. |

Portable validation must name exactly one input: the Git index or a specified commit tree. It checks that tree's bytes, modes, manifest reachability and reference availability; it must not mix worktree files into a staged-tree verdict. Local validation separately reports untracked/ignored files and uncheckpointed edits. Both profiles work without runtime state or a session database.

Sealed metadata/snapshots require byte-preserving Git storage and checkout behavior. Inspect applicable attributes, line-ending conversion, clean/smudge filters and LFS treatment; refuse a portability claim when captured bytes differ from staged/committed blobs. A byte-preservation policy, if needed, is a separately declared implementation change. Do not silently edit `.gitattributes`, stage files or run arbitrary content filters during validation. Mutable working documents may follow the repository's usual text policy, but a closed case's permitted inventoried working files must also exist and match their hashes in the selected tree, including files omitted from the evidence claim. Normalize/recapture before closing if conversion would change those bytes; do not waive an integrity mismatch as a harmless line-ending difference. Disposable unversioned output belongs outside that retained working set.

CI also receives an explicitly identified trusted base tree and proposed tree from its existing integration owner. Enumerate managed cases in **both**: otherwise deleting an entire case bypasses validation. Require the proposed receipt chain to extend the base chain, every formerly sealed record/object to remain byte-identical and reachable, and case identity/path to remain stable. New cases receive full validation; unsupported case deletion, history truncation/rewrite, duplicate identity and divergent ancestry fail. Do not trust a base revision supplied only by the case author. If the base is unavailable, report incomplete history validation rather than pass. No network fetch is needed or authorized by the validator.

This comparison detects rewrites relative to that trusted base; it is not cryptographic producer authentication. A self-contained chain with no trusted predecessor can demonstrate internal consistency only. Direct edits and private branch copies remain outside preventive coverage. A future intentional migration/redaction must define its own reviewed exception and evidence invalidation; V1 has none.

Proposed generated rule after V1 adoption:

> For an adopted sandbox case, use the current version for lifecycle changes, keep working artifacts within its scope, and checkpoint at handoff. Case evidence never grants execution or implementation authority. Respect explicit file-only requests and existing workflow/project ownership; use `omt_sandbox` guidance on demand.

Do not demand a new case for every review, a checkpoint after every edit, or a second approval for a user instruction that already covers the intended action. Preserve workflow approval boundaries for **additional** work. An “override OMT” recipe is not a machine-verifiable capability to bypass case integrity or protected-file rules.

### 6.2 Optional future editor gate

A proposed `g.sandbox` at order 38 would be after `g.net`/`g.split_proof` and before phase/thought checks. **Its declaration and activation are deferred.** If adopted, it validates only configured managed surfaces, runs independently of the net's single-session shortcut, and never makes all of `.sandbox/` a harness-receipt surface.

Before implementation approval, resolve and test:

1. **Target extraction.** Enumerate every source and destination of edits, writes, multi-file patches, renames, moves, and deletes. Current `edit|write|patch|multiedit` names and single-path extraction are not a complete inventory. Unknown target shapes must be refused in opt-in strict mode or explicitly reported as uncovered in advisory mode.
2. **Containment.** Resolve the repository/worktree and nearest existing parents. Stored case paths and service artifact arguments are relative; host edit tools may supply absolute paths, which must be normalized and verified inside the correct checkout before evaluating their owning scope. Reject traversal, cross-case aliases, symlink components and nested repository/worktree entry through a parent. Reject hard-linked managed files for controlled replacement. Service writes need no-follow/exclusive operations and commit-time revalidation; a pre-hook `realpath` alone cannot prevent a symlink-swap race.
3. **All obligations compose.** Keep protection, receipt, canary, net, phase, thought, KB, and after-edit obligations intact for every affected path. Case metadata is never a bypass for writes outside its artifact area.
4. **Projection parity.** The current live loop continues after a gate returns `stop`; `runBeforeGatesDry` breaks. Resolve relevant parity gaps or describe them explicitly before claiming that preflight proves the live decision. Update fallback gate tables and clearing actions as well as the IR declaration.
5. **Mutation bypasses.** CLI/service writes validate internally, regardless of editor hooks. Shell commands, foreign editors, and arbitrary scripts are not confined by command-name matching. A hook can authorize all targets before an edit, but it cannot promise rollback/atomic application by a third-party patch tool.
6. **Immutable versus mutable files.** Protect tool-owned metadata and sealed objects at covered boundaries; ordinary working drafts stay editable while active. Out-of-band changes are detected by validator/CI according to artifact class. Hashes are not adversarial tamper-proof storage.

Publish a coverage matrix per host/tool version: preventive, detective, or unsupported. This includes the actual tools exposed to the agent; an OpenCode hook cannot be assumed to intercept another host's `apply_patch` or shell writer. Freeze or snapshot a managed input set before sealing it; do not claim a consistent snapshot of an arbitrarily changing repository.

Reserved `.sandbox/bench/` and any Git-discovered checkout delegate to their execution owner. Artifact APIs reject entry through a parent path. `.runs/` belongs to a declared case/run but gets output from an authorized executor; the lifecycle service is not itself that executor.

### 6.3 Integration and budgets

| Surface | Scope if adopted | Stage |
|---|---|---|
| `.meta/META_HARNESS.omt` / `harnessc.py` | Static subject set, contract version, tool/nav declaration and budget parity; no dynamic case or session reads in compilation. | Conditional V1. |
| Sandbox service / adapter / harness CI | Shared bounded validator, storage protocol, transport parity, portable-tree and history-delta checks. | Conditional V1. |
| `omt_nav` | Contract/lookup entry point only, not case or evidence payloads. | Conditional V1. |
| Shared ledger | Optional correlated `sandbox_*` mirrors, explicit delivery status, deduplicating consumers; preserve existing authority-write behavior. | Add only for a demonstrated consumer; not a V1 correctness dependency. |
| `omt_status` / preflight / `omt_q` | Relevant bounded summary from a pure decision function/snapshot; no status-side mutations or execution. | Later integration, if useful. |
| `omt_complete` | Validate explicitly referenced sandbox evidence; closing a case never finishes a feature. | Later owner integration. |
| Net / session / experiment tooling | References only; no duplicate claims, lease service, raw session store or launcher. | Preserve boundary in every stage. |
| Projects / toolbox | Destination-owned transfer and consumer updates; no duplicate lifecycle or direct uncoordinated SQLite edits. | Later promotion/migration. |
| `.gitignore` / Git attributes | Narrow staging/runtime/output exclusions and explicit byte-preservation policy for sealed files; account for existing `*.log` ignores. | Conditional V1, as declared changes; no blanket sandbox ignore. |

The inspected DSL has **11 formal tools, 11 gates, and a gate cap of 12**. The convention pilot adds neither. Conditional V1 would add one tool and no gate. A later twelfth gate is within the compiler's numeric cap but triggers its at-cap warning; the DSL also states net-zero retirement/merge guidance. Treat those as distinct facts. A policy exception or a proven consolidation needs an explicit decision; neither is preapproved by this document. Do not retire an unrelated guard just to make the count look acceptable.

Measure generated instruction bytes, description/schema bytes, IR/nav growth, response sizes, and actual calls/tokens. `tool_schemas`, `tool_args`, `agents_md`, `ir_json`, and `nav_index` all have existing caps. Keep operation details behind on-demand help and do not hide a budget increase in generated output. No dynamic catalog data belongs in conversation startup by default.

## 7. Representative flows and promotion boundary

### Existing one-file proposal review

Read the named file and relevant sources; improve that file within the user's scope. A future case system may advise registration, but it must not create manifests, rewrite `WORK.md`, or close a project merely because the user requested a review. This delivery follows that constraint.

### Opt-in new proposal

For the convention pilot, write one ordinary proposal with owner, purpose, status and a next action. If the service is later adopted, reuse the current case or allocate its stable ID before `create`, draft inside it, and close with a pinned final inventory. `close` captures/validates the final checkpoint internally. Inspection to obtain a fresh inventory is a real cost and must be counted; do not conceal it by calling the flow “two calls.” “Completed analysis” is not “approved implementation.”

### Workflow investigation and pause

Read the catalog, subject manifest, and selected recipe. Reuse, explicitly resume or create a case if that workflow has adopted cases. Record the recipe digest and findings; honor its approval boundary for new work. `checkpoint(pause=true)` seals a handoff. Existing workflow/project/net owners still decide whether to update `WORK.md`, pause a claim, or release resources. A sandbox pause must not falsely announce that those independent actions succeeded.

Resume by inspecting the checkpoint, refreshing Git/net/project state, and explicitly resuming. Conflicting historical summaries remain visible; newest filename or newest wall-clock timestamp does not decide current authority. Missing external links or incompatible current policy are reported before further lifecycle writes, not repaired by replaying old instructions.

### Experiment

Keep exploratory code/selected inputs in the case. Run only through an already available authorized mechanism; register selected results with observation class and limitations. An output can be intact but irreproducible because dependencies or dirty source were not captured. Surface that distinction instead of inventing a passing receipt.

### Later promotion contract

Promotion is an owner-mediated transfer/link decision, not execution of a proposal's instructions. Some promotions merely link an accepted design into an existing project; they do not all need a new feature or a bulk copy.

A future plan must identify source snapshots/hashes, destination owners, exact writes/links, absence or hashes of destination files, required owner gates, expected versions, and outstanding validation. Planning is read-only and consumes no new IDs with lasting effects. Persisting the plan, if requested, is a separate declared write.

Apply may use existing authorization when it covers those effects. Ask again only for uncovered scope or material plan changes. If mechanical approval verification is claimed, define the trusted host/owner issuer, receipt format, scope, freshness, consumption/replay rules, and failure behavior. An agent-writable file or boolean is insufficient; do not claim a trust boundary unavailable in this local environment.

Use sequential owner operations with durable step receipts. If project creation succeeds and a later link fails, record **partial**, reconcile through that owner, and leave the case unpromoted. Only verified completion sets the promoted disposition. Copied source evidence remains; destination content gets its own identity/validation. A failed compensation never turns a partial promotion into a success.

## 8. Migration plan

These are classification candidates, **not an executable move list**. Keep legacy content usable until each ownership group has a reviewed map and working consumers. No migration is part of this delivery.

| Existing material | Destination/treatment candidate |
|---|---|
| `.sandbox/meta/improvement001..007/` | Distinct `meta_harness` cases; preserve iterations, decisions and outcomes. |
| `sandbox/meta/improvement*`, `sandbox/meta/remove_tui/` | Independently identified cases; inspect `remove_tui` ownership. Never merge by suffix. |
| Root `meta_harness_*`, `category_theory_meta_harness.md`, `.sandbox/meta/META_HARNESS_CONCURRENT_NEXT_STEP.md`, `sandbox/META_HARNESS_*.md` | Harness proposal/investigation cases with explicit lineage; no newest-filename inference. |
| `.sandbox/harness_reason/` | Retain initially. Move maintained fixtures/resolvers into their maintained subsystem with its tests first; preserve experimental history separately. |
| `.sandbox/global_state/`, `frontier/`, `work_contract/` | Separate experiment cases; classify scripts and outputs after consumer discovery. |
| `.sandbox/b2_mig_snapshot/` | Historical bundle attached to its migration activity; never load it as current net state. |
| `.sandbox/proposal/`, `tests_folder_refactor_proposal.md`, `sandbox/orthogonality_001_wrapper_split/` | Harness-owned cases with project links and V7/V8/V9 lineage. Do not execute proposed code/test moves. |
| `sandbox/consistency_enforcement/` | Agentx workflow case(s), preserving rounds and probe/test ownership. |
| `.sandbox/feature_024_console_parity_bugs.md`, `feature_typesafe_jev_decision_layer*` | Agentx investigation/proposal cases after classification. |
| `.sandbox/akb_smart_population_and_update/` | App-knowledge-base case preserving round history. |
| `pause_*.md`, `r8_resume_*.md`, `session_*.md`, embedded `RESUME.md` | Attach to identified activities. Unknown ownership remains visible legacy debt; historical notes do not become verified current checkpoints automatically. |
| `.sandbox/toolbox_proposals/` | Retain under toolbox ownership. Later update both proposal-file creation and stored `draft_path` through a toolbox-owned migration adapter. |
| `.sandbox/bench/`, other Git-discovered worktrees | Excluded from artifact migration/index recursion; preserve execution ownership. |
| This proposal | Import only if adoption/migration is later authorized. |

Migration requirements:

1. **Fresh bounded inventory.** Record path, file type, permitted content hash, mode, Git tracked/staged/untracked/ignored status, owning worktree, source activity, and known inbound references. Include both roots and relevant consumer stores. Inspect names/types before reading; protected/unsafe exclusions have no content hash. Do not follow links into worktrees, secrets, or unrelated directories. Record uncertain ownership and ignore rules explicitly.
2. **Exact accounting.** Each source gets one disposition: moved, retained by a named owner, preserved as history, or compatibility artifact. Identical bytes are not grounds to merge different provenance. A mutable legacy source cannot serve as a sealed evidence copy.
3. **Worktree/writer preconditions.** Check relevant net claims and quiesce affected writers through their owners; take supported local operation locks for managed cases. Capture hashes for every touched source, destination and consumer plus the relevant Git index state. Refuse stale plans and destination collisions. Unrelated dirty files do not have to be discarded or committed.
4. **Documentation pilot first.** Pick one closed, unconsumed documentation group. Preserve bytes where possible; if links must change, retain the old snapshot plus an explicit transformation map. Verify relative links from their new directory, anchors, Markdown entry points and code/path references. A tracked `git mv` and an untracked file move have different index effects; plan both explicitly. Do not stage unrelated changes.
5. **Current pointers versus history.** Update active workflow declarations, current project pointers and `WORK.md` only when the authorized migration includes them. Preserve old immutable notes and resolve their references with explicit aliases. An alias lookup and a Markdown redirect cannot satisfy `open(old_path)` or an existing SQLite `draft_path`.
6. **Maintained consumers separately.** Move reasoning fixtures/resolvers with targeted regression checks. Toolbox needs a recoverable filesystem-plus-database protocol under its owner. If an owner has no suitable adapter, retain the old path until one exists; do not pretend the sandbox journal controls its database.
7. **Compatibility without ambiguity.** Legacy aliases must be unique or return an ambiguity error. Markdown redirect stubs can preserve human entry points; never substitute prose for JSON/code. Record a removal criterion per alias. Do not rewrite arbitrary prose or immutable evidence merely because a search finds an old path.
8. **Recover stepwise.** No cross-filesystem move is advertised as atomic: copy, verify, update owner references, then remove only the expected source if authorized. Store before/after digests and step receipts. Rollback/compensation can revert a file only if it still matches the migration's after-image; otherwise stop and report conflict. A reverse map alone is insufficient. Never use repository-wide `git reset` to recover.
9. **Retire the second root last, if practical.** All executable consumers must resolve and all remaining compatibility/history paths have named owners. If stubs are intentionally retained under `sandbox/`, describe canonicalization as complete and root deletion as incomplete; do not claim both. Deletion is a separate scoped action, not automatic garbage collection.

The pilot need not resolve every historical note. Migration is complete for a group when accounting balances, consumer/link checks pass, runtime ownership is intact, and recovery has been demonstrated. Wider enforcement must not erase unresolved legacy debt from reports.

## 9. Delivery slices and decision criteria

| Slice | Deliverable | Exit evidence / decision |
|---|---|---|
| A — baseline and convention pilot | Measure current discovery/resume/document-review tasks; try option A on one proposal and one real handoff. No new tool, gate or migration. | Record task correctness and total effort. Stop at conventions if they meet the need. |
| B — service go/no-go | Identify failures left by A; choose the smallest required capabilities, numeric limits, supported filesystem and responsible maintainer. Allocate feature/project only when implementation is requested. | Explicit evidence that selected snapshots/recovery/validation address an observed failure; agreed cost bounds. No automatic progression to code. |
| C — conditional V1 | First schema/read-only validation, then local transactional mutations/capture/recovery, then the thin adapter and portable/history CI checks. | Crash and race checks, transport parity, bounded work/results, absence of product dependency, and effect-free reads. No leases, migration or editor gate. |
| D — service pilot | Re-run matched tasks with one new proposal, one real pause/resume and an explicitly authorized historical copy. Retain legacy originals; no import/migration apply. | Compare correctness and total cost against A. Keep optional, simplify, or stop if benefit is absent. |
| E — destination integrations | Separate owner-reviewed migrations: closed documentation first, then maintained reasoning/toolbox/project/workflow consumers where justified. | Consumer regression checks and partial-operation recovery; no executable old-path breakage. |
| F — optional enforcement / retirement | Scoped preventive coverage or legacy-root retirement, each with its own decision. | Coverage canaries, live/preflight parity, budget/split proofs, and separately satisfied retirement criteria. |

The baseline must include a successful and a failed artifact lookup, a resume after session loss, and an explicit one-file review. For each, record the correct artifact, actual next action, supporting evidence and evaluator rubric **before** comparing alternatives. A stale resume that confidently follows the wrong task fails even if it is fast.

Measure all relevant work: manual edits, discovery reads, successful/failed tool calls, prompt/schema/response tokens, elapsed task and service time, recovery effort, stored bytes, and ongoing maintenance obligations. Include source-inventory reads needed to pin captures. Report machine/corpus, sample size and synthetic/live labels. Use matched comparable tasks or counterbalance order; repeated execution by an agent that already knows the answer is not an unbiased search baseline. A few examples demonstrate feasibility, not a population-level performance result.

Before running a comparison, agree which unmet outcome justifies the service and its acceptable total cost. The default decision is to retain conventions unless option B improves a preselected outcome without a correctness regression and stays within those declared costs. Do not expand solely because cases can be created and closed successfully.

Proposed acceptance criteria for conditional V1:

- Ordinary product edits and explicit file-only reviews require **zero additional mandatory calls or files**.
- A new one-document opt-in case targets three service calls on a clean path: `create`, final `inspect` for the pinned inventory, and `close`. Count all additional reads/retries; a caller already holding verified input hashes may omit inspect.
- Same-checkout concurrent operations serialize; every tested interruption produces the original committed receipt, an uncommitted prepared attempt or an explicit indeterminate/conflict result. No authored bytes are lost and a retry creates no duplicate reachable transition.
- Branch-divergence, whole-case deletion and rewritten sealed history fail the base-to-proposed-tree check. V1 does not claim global single-writer coordination.
- A committed pilot case passes portable-tree validation in a clean clone without local caches, locks, session databases or ignored journals. A missing trusted base allows integrity inspection but not a successful history-delta verdict.
- Unrelated worktree contents and existing gates remain unchanged by case operations. Dynamic cases do not add startup instructions or tracked navigation records.
- Routine list/inspect summaries target 2 KiB; input, scan, history and storage bounds are independently exercised. Oversize details have explicit pagination/reference contracts. Set a latency target only after measuring the supported machine/corpus.
- Publish the observed discovery/resume correctness, all added costs and failure outcomes. If ordinary users incur new ceremony or the service gives no demonstrated benefit over conventions, revise or stop instead of adding a gate to force adoption.

At implementation time, follow applicable phase/TDD, canary, receipt, compiler and split-proof procedures. These are not executed or marked complete by this document review.

## 10. Required implementation acceptance checks

These are proposed behavior checks, not tests written or results claimed in this delivery. Only the conditional V1 rows are release requirements for V1; the later matrix applies when those capabilities are separately proposed.

| Conditional V1 area | Required positive and negative cases |
|---|---|
| Schema/metadata | Minimal proposal; optional links; allowed owner correction; unknown fields, duplicate JSON keys, unknown schema, invalid transitions and external scope expansion rejected. Scope narrowing accounts for existing files. |
| Identity/versioning | Same revision/different digest refuses; creation retries reuse the caller ID; duplicate ID across subjects refuses; incomplete census cannot certify uniqueness; title changes preserve identity/path. |
| Operation locking | Two processes mutate the same physical case; subdirectory invocation resolves the same root; process crash releases lock; a busy live lock is not deleted/expired; unsupported locking refuses. Separate worktree copies are not advertised as synchronized. |
| Capture races | Draft changes without manifest change; selected path added/deleted during close; path replaced during copy; copied hash differs from request; two-file skew correctly labeled; no coherent-snapshot claim from per-file checks. |
| Idempotency | Retry after commit/timeout returns original core receipt and current version separately; changed payload conflicts; partial attempt reconciles; changed draft after refusal cannot be silently recaptured under the old request. Rewound/branched history limits are explicit. |
| Crash/durability | Fail before/after each object, record, manifest replacement and directory flush; fail response/mirror; disk full; lost staging/journal. Verify no false committed/refused result where commitment is unknown. Staging on another filesystem cannot be used for atomic publication. |
| Mutable/immutable boundary | Draft edits after checkpoint remain ordinary uncheckpointed work; snapshots preserve old bytes; closed inventory changes are detected; validator never blesses edited evidence by recomputing the baseline. |
| Evidence meaning | Unexecuted, historical, synthetic and redacted results; uncaptured dirty inputs; unavailable external evidence; unknown versus failed claim validation. No passing result or permission inferred from a filename, digest or zero exit code. |
| Safe paths/content | Traversal, absolute paths, symlink/parent swaps, hard links, devices/FIFOs, nested checkouts, bench paths and protected names. Verify protected content is never opened, even for hashing. Include case/Unicode path collisions on supported filesystems. |
| Bounded work/storage | Oversized manifest/request, many tiny files, deep/cyclic receipt history, full evidence quota, staging quota, catalog limit and concurrent pagination change. Closure allowance and deduplication are explicit; partial scan never becomes pass/not-found. |
| Portable-tree profile | Index bytes differ from working bytes; ignored/untracked/missing references; clean/smudge/LFS/line-ending transformations; file modes/types; no runtime/session state. Do not mix trees. |
| History-delta profile | Entire case deletion; dropping old record/object; rehashing an entire chain; divergent equal-revision branches; duplicate IDs; absent/untrusted base; clean fast-forward. Unchanged sealed history stays byte-identical/reachable. |
| Responses/effects | Read operations create no files/logs/locks; refused mutation distinguishes runtime lock effects; partial publication lists staged/orphan paths; complete write details are retrievable; mirror duplicates are deduplicated and mirror failure cannot revoke commit. |
| Boundary/transport | Plugin/CLI request parity, literal argv and coerced JSON, missing policy, existing harness constraints; no project/net/feature completion by case close; product builds/tests without the sandbox service. |
| Adoption/cost | Docs-only work counted; convention baseline retained; dynamic catalogs absent from compiler/startup; real schema/token/storage costs measured; optionality and narrow user scope preserved. |

| Later capability | Additional acceptance required before adoption |
|---|---|
| Editor gate | Actual host edit/patch/move/delete shapes; all targets checked; unknown forms handled by declared mode; live/preflight parity; protected/phase/think/test/KB obligations preserved; shell/foreign-editor coverage honestly labeled. |
| Shared writer coordination | Sequential stale-worktree counterexample as well as simultaneous writers; durable common tip, branch switch/removal, coordinator loss, fencing and clone boundary. No reuse of V1 local-lock claims as proof. |
| Import/migration | Tracked/untracked/ignored files, dirty index, duplicate suffixes, relative links/anchors, unique aliases, JSON/code consumers, toolbox database/file failures, compensation after subsequent edits. Ownership accounting balances. |
| Promotion/exception/removal | Destination-owner authority and receipts; plan-only creates no records; partial transfer never reports success; intentional history migration/redaction has a reviewed CI exception and explicit evidence invalidation. |
| Persistent cache | New/removed/corrupt manifests cannot remain hidden; stale cursors are detected; effect-free reads and explicit rebuild; bounded work established independently of response size. |

## 11. Source references and verification of this delivery

Primary local references used:

- [Harness policy, paths, lifecycle, gates, tools and budgets](../.meta/META_HARNESS.omt), [harness vision](../META_VISION.md), and [compiler budgets/ceremony implementation](../scripts/omt/harnessc.py).
- [Enforcer composition and target extraction](../.opencode/plugins/omt_enforcer.ts), [live/dry gate driver](../.opencode/lib/enforcer/gate_driver.ts), [preflight projection](../.opencode/lib/enforcer/preflight.ts), and [phase/completion behavior](../.opencode/lib/enforcer/phase_gate.ts).
- [Shared ledger, rotation and transport helpers](../.opencode/lib/omt_shared.ts), [ignored runtime/evidence patterns](../.gitignore), and [ceremony/budget behavior tests](../tests/features/feature_057.gate_budget_ceremony_meter/test_gate_budget_ceremony.py).
- [Net adapter](../.opencode/plugins/omt_net.ts), [session adapter](../.opencode/plugins/omt_session.ts), [session service](../scripts/session_inspect/service.py), and [read-only SQLite adapter and bounded-selector contract](../scripts/session_inspect/adapter.py).
- [Workflow catalog](../.workflows/META.md), [harness workflow manifest](../.workflows/meta_harness/META.md), and [pause recipe](../.workflows/meta_harness/pause_dev_for_resume_later.md).
- [Worktree lifecycle and both lanes](../scripts/omt/net/worktree_lifecycle.py), [benchmark sandbox owner](../scripts/omt/bench/sandbox.py), and [existing net gate](../scripts/omt/net/gate.py).
- [Reasoning resolver](../.opencode/plugins/reason_table.ts), [fixture consumer](../tests/scripts/reason/test_probes_fixtures.py), and [toolbox proposal producer/database path storage](../scripts/toolbox/toolbox.py).
- [Reasoning experiment](harness_reason/stage0_probes.md), [legacy improvement](meta/improvement001/CURRENT_STATE.md), [distinct net-enforcement activity](../sandbox/meta/improvement001_net_enforcement/IMPROVEMENT_OPTIONS.md), [pause note](pause_2026-10-10b.md), and [wrapper-split proposal family](../sandbox/orthogonality_001_wrapper_split/README.md).

Delivery verification is recorded after the final document checks. The JSON examples are illustrative, not validated receipts. No runtime feature has been implemented, benchmarked, migrated, approved or completed. No application test run is claimed for this document-only change.
