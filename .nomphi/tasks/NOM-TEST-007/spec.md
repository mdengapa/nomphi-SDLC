# Technical Specification

Status: COMPLETE

## Objective

PROPOSED: Enforce the human-approved `project_id` contract at explicit project initialization, project-adapter validation, task creation, and every existing task-state load. Runtime must reject invalid identifiers, attempts to replace an established valid identifier, and task state whose copied identifier differs from the current project profile.

## Evidence / grounding

- `.nomphi/core/manifests/planner.md` — canonical planning contract for evidence, proposals, unknowns, status, and unchecked proof obligations.
- `.nomphi/tasks/NOM-TEST-007/requirement.md` — human-approved source-of-truth, format, immutability, exact-copy, initialization, and mismatch-rejection decisions.
- `.nomphi/tasks/NOM-TEST-007/handoff-planner-planning.md` — historical handoff snapshot for this PLANNING iteration; its uppercase identifier snapshot differs from the current canonical files.
- `.nomphi/project/project-profile.json` — current canonical project profile; it contains the valid identifier `nomphi-sdlc`.
- `.nomphi/tasks/NOM-TEST-007/state.json` — current task state; it contains the same `nomphi-sdlc` identifier and remains in PLANNING.
- `.nomphi/project/README.md` — defines the project adapter as project-specific and identifies the profile as identity configuration.
- `.nomphi/project/architecture.md`, `.nomphi/project/domain.md`, `.nomphi/project/invariants.md`, `.nomphi/project/conventions.md`, and `.nomphi/project/security-boundaries.md` — currently contain placeholders and add no further identifier contract.
- `.nomphi/project/commands.json` — configures no project test, typecheck, lint, E2E, or security commands.
- `scripts/nomphi.py` — current adapter validation, project initialization, task creation/loading, task-ID validation, workflow commands, and JSON persistence.
- `scripts/nomphi_agent.py` — agent API; it delegates adapter/task handling to `scripts/nomphi.py` and does not expose project initialization.
- `.nomphi/core/schemas/project-profile.schema.json` — requires a non-empty string `project_id` but does not encode the approved format.
- `.nomphi/core/schemas/task-state.schema.json` — requires a non-empty string `project_id` but cannot encode equality with a separate profile document.
- `bootstrap.sh` — accepts caller-supplied `--id`, copies the current project adapter into a new target, and then invokes `project-init`.
- `tests/test_nomphi.py` — existing `unittest` subprocess coverage uses uppercase project-ID fixtures, expects the source profile to be `REPLACE_ME`, and verifies task-state copying only for the current permissive behavior.
- `Makefile` — repository test command is `python3 -m unittest discover -s tests -v`.
- `README.md` — documents bootstrap with an uppercase project-ID example and describes the copied adapter as blank.
- `examples/generic-fullstack/project/project-profile.json` and `examples/cuadra/project/project-profile.json` — optional example adapters contain identifiers that do not satisfy the approved format.
- `ARCHITECTURE.md` and `docs/CORE_VS_PROJECT.md` — place reusable workflow rules in core and project-specific identity/context in the project adapter.

## Existing context

The requirement, rather than the task-ID validator or repository examples, is authoritative for project-ID rules:

- `project_id` is the stable canonical identifier of a Nomphi project.
- `.nomphi/project/project-profile.json` is its source of truth.
- The exact approved format is `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Every task must copy that exact value into its `state.json`.
- The value is immutable for the project's lifetime and is independent of project name, repository name, and directory name.
- Agents may read but may not invent, derive, rename, or modify canonical project identity.
- Establishing identity for a project without a valid value requires an explicit human decision.
- Runtime must reject task state whose value differs from the profile.

Current behavior and gaps supported by `scripts/nomphi.py`:

- `validate_adapter()` rejects only missing/JSON-null, empty, and exact `REPLACE_ME` values; other types or malformed strings can pass.
- `init_project()` writes before adapter validation and can overwrite an already valid identifier.
- `task_init()` already copies `pr['project_id']` exactly after adapter validation.
- `state()` verifies `task_id` but does not validate or compare `project_id`.
- `status` and `next` load state without independently validating the adapter; other task commands validate the adapter but still do not enforce profile/task equality.
- Runtime does not execute either JSON Schema.
- The independent `TASK_ID` regex permits uppercase and underscore and must not be reused as a project-ID rule.

The historical handoff is not the project identity source of truth. Its `NOMPHI-SMOKE` snapshot is stale relative to the current profile and task state; this task does not rewrite historical handoffs.

## Scope

PROPOSED:

- Add one canonical project-ID lexical validator in `scripts/nomphi.py`, independent of `TASK_ID`.
- Validate explicit initialization input before persistence and prevent `project-init` from changing an established valid ID.
- Validate adapter-loaded profile IDs.
- Compare each loaded task state's project ID exactly with the current valid profile ID.
- Preserve the existing exact-copy behavior for new tasks.
- Align both JSON schemas with the approved lexical format.
- Adapt bootstrap so a copied donor profile is explicitly uninitialized in the new target before the caller-supplied ID is established.
- Update existing tests and add format, immutability, copy, mismatch, and bootstrap regression coverage.
- PROPOSED: In the documentation stage, align the bootstrap example and blank-adapter description with the implemented flow.

## Out of scope

- PROPOSED: Do not change `TASK_ID`, `valid_task()`, task directory naming, or any task-ID acceptance behavior.
- PROPOSED: Do not derive identity from task ID, project name, repository name, directory, or an old invalid value.
- PROPOSED: Do not trim, lowercase, normalize, migrate, or silently rewrite identifiers.
- PROPOSED: Do not add a second persistent identity source, network service, UI, third-party dependency, or project-initialization operation to `scripts/nomphi_agent.py`.
- PROPOSED: Do not alter workflow transitions, routing, risk handling, unrelated profile fields, current `.nomphi/project/project-profile.json`, or current task state.
- PROPOSED: Do not assign replacement IDs to optional example adapters; agents lack authority to invent those identities. They remain documented compatibility examples outside runtime paths installed by `bootstrap.sh`.
- PROPOSED: Do not rewrite historical handoff snapshots.

## Architecture affected

The existing deterministic workflow helper remains the enforcement boundary. The project adapter remains the sole canonical persistence location, while task state remains a copied value checked against that source on load. JSON Schema expresses each document's lexical constraint; runtime code enforces the cross-document relationship that JSON Schema cannot express here.

PROPOSED: Bootstrap must distinguish donor configuration from target identity. After copying `.nomphi/project/` into a target that passed the existing no-core-overwrite guard, it must set only the target copy's `project_id` to the existing uninitialized sentinel before calling `project-init` with the caller's explicit value. It must not mutate the source repository profile or derive the target ID from donor metadata or target paths.

## Files/modules likely affected

- `scripts/nomphi.py` — PROPOSED: lexical validation, write-before-validation fix, initialization immutability guard, and centralized task/profile equality check.
- `.nomphi/core/schemas/project-profile.schema.json` — PROPOSED: replace the weaker length-only project-ID constraint with the approved pattern while retaining string typing.
- `.nomphi/core/schemas/task-state.schema.json` — PROPOSED: apply the same lexical pattern; equality remains a runtime check.
- `bootstrap.sh` — PROPOSED: stage only the target's copied profile as uninitialized before explicit initialization.
- `tests/test_nomphi.py` — PROPOSED: replace invalid runtime fixtures and add decision-table and subprocess regression coverage.
- `README.md` — PROPOSED: documentation-stage alignment only, after behavior is verified.
- `scripts/nomphi_agent.py` — no production change proposed; integration tests must verify delegated task loads fail closed.

## Data model

Existing profile and task-state schemas both require `project_id` and type it as a string. The approved cross-document invariant is recorded in the requirement.

PROPOSED: In both schemas, `project_id` remains a required string and receives the exact anchored pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`. No maximum length is added because none is approved. Schema validation does not replace runtime validation and does not establish cross-file equality.

The approved expression permits one or more lowercase ASCII letter/digit segments separated by one hyphen. Consequently, it permits a single segment and digits-only segments, and rejects empty strings, uppercase, underscore, whitespace, Unicode outside the listed ASCII ranges, leading/trailing hyphens, and repeated hyphens. These consequences come from the approved expression, not from task identifiers or example values.

## Interfaces / contracts

PROPOSED:

- Add a side-effect-free project-ID predicate that returns true only for Python strings fully matching the approved expression. It must not transform input and must not call or reuse `valid_task()` or `TASK_ID`.
- `validate_adapter()` must reject missing, `null`, boolean, numeric, array, object, sentinel, empty, and nonmatching profile values with a `HUMAN_DECISION_REQUIRED` initialization error.
- `project-init --id` remains the explicit human-facing initialization interface. It must validate the supplied candidate before any profile write.
- If the stored profile ID is valid, `project-init` may proceed only when the supplied ID is exactly equal; a different candidate must reject the entire update before persistence. Equal-ID calls may retain existing behavior for updating name, type, and risk.
- If the stored profile ID is absent or invalid, a direct caller-supplied valid ID may establish it exactly. The agent wrapper continues not to expose this interface.
- `state()` (or an equivalently central existing load boundary used by every task command) must load a valid profile and reject a missing, malformed, or unequal task `project_id` before returning state.
- Rejections exit nonzero. Initialization rejection emits no success message and leaves the pre-call profile bytes unchanged. Task-load rejection performs no task-state or task-artifact write.

## Functional flow

### Explicit initialization

PROPOSED:

1. Read the current profile without modifying it.
2. Validate the caller's original `--id` value exactly.
3. If the current ID is valid, require exact equality with the caller value.
4. On any failure, exit before writing any profile field.
5. If the current ID is absent/invalid or equal, retain the exact caller/current ID while applying the existing metadata updates and writing once.
6. Re-run adapter validation before reporting success.

### Bootstrap of a new target

PROPOSED:

1. Retain the existing refusal to overwrite a target containing `.nomphi/core`.
2. Copy the installation files.
3. In the target only, stage the copied profile ID as `REPLACE_ME`, preserving other copied fields until existing initialization updates them.
4. Invoke `project-init` with the exact caller-supplied ID.
5. Invalid input leaves no valid target identity and exits nonzero; source identity remains unchanged. Valid input establishes the target ID exactly.

### Task creation and loading

PROPOSED:

1. Task creation validates the adapter and copies `pr['project_id']` unchanged, as it does now.
2. Every later call to `state()` validates the current profile and then loads the task state.
3. Existing `task_id` integrity validation remains unchanged.
4. Missing, non-string, malformed, or unequal task `project_id` rejects before command-specific output or mutation.
5. Equal valid values allow existing task behavior to continue.

## Invariants

- The profile is the sole canonical persistent source of project identity.
- Project ID is independent of task-ID syntax and naming/path metadata.
- Agents do not choose or edit canonical project IDs.
- PROPOSED: Controlled runtime paths never normalize or derive identity.
- PROPOSED: `project-init` never replaces one valid ID with a different ID.
- PROPOSED: New tasks copy the validated profile value byte-for-byte.
- PROPOSED: No task with missing, malformed, or unequal project identity proceeds through a task command.
- PROPOSED: Bootstrap modifies only the new target copy while establishing the human-supplied identity; it never modifies the donor profile.

Because the profile is the only canonical identity record, runtime cannot detect an out-of-band profile edit in a project with no task copy to compare. Such edits remain prohibited by the approved operational invariant; this change adds no second source merely to detect them.

## Edge cases

PROPOSED: Cover at least these categories without treating samples as naming rules:

- valid grammar boundaries: one segment, numeric segment, mixed lowercase/digit segment, and multiple segments;
- invalid strings: empty, uppercase/mixed case, underscore, punctuation, slash/backslash, whitespace, leading/trailing/repeated hyphens, control characters, and non-ASCII characters;
- invalid JSON types: `null`, boolean, number, array, and object;
- the existing `REPLACE_ME` sentinel;
- a conforming long value, because no maximum length is approved;
- same-ID reinitialization and different-valid-ID replacement;
- missing, malformed, and different-valid task IDs at the `project_id` field;
- unrelated project name, repository directory, and task ID values, proving no derivation;
- stale handoff content, proving historical snapshots are not consulted as identity authority.

## Failure modes

- Validation after `write_json()` can persist an invalid or changed identity before rejection.
- Reusing `TASK_ID` would reject approved lowercase values and import unrelated task-path rules.
- A comparison only in adapter-gated commands would leave `status` and `next` accepting invalid task state.
- Normalization would turn invalid input into an unapproved identity.
- Tightened schemas and runtime checks will reject historical profiles previously accepted by permissive code.
- Copying the donor's valid profile unchanged and then enforcing immutability would block bootstrap for a different target ID; target-side uninitialized staging prevents that conflict.
- Bootstrap can remain partially installed after initialization failure, as it can today; the target must remain fail-closed with no valid assigned identity.

## Security-sensitive areas

Existing inspected runtime uses `task_id`, not `project_id`, for task paths. `project_id` is stored in JSON and included in status/gate output; no inspected code uses it to construct paths or shell commands.

PROPOSED:

- Keep project identity out of path and subprocess-command construction.
- Reject identity inconsistency before task mutation, handoff generation, gate command execution, or success output.
- Error messages may identify the field and failure class but must not dump unrelated profile or task contents.
- Preserve the existing task-ID path-safety validation unchanged.

## Acceptance criteria

- [ ] PROPOSED: Runtime accepts a project ID if and only if it is a string fully matching `^[a-z0-9]+(?:-[a-z0-9]+)*$`, with no normalization or added maximum length.
- [ ] PROPOSED: Project-ID validation is independent of `TASK_ID`; all existing task-ID behavior remains unchanged.
- [ ] PROPOSED: Invalid `project-init` input and attempts to replace a valid ID fail before any profile write or success message.
- [ ] PROPOSED: An equal-ID `project-init` call retains the exact ID and may update the existing non-ID metadata fields.
- [ ] PROPOSED: An uninitialized/invalid profile can receive an exact valid ID only through the explicit initialization interface.
- [ ] PROPOSED: Name, repository name, directory, and task ID never derive or alter project identity.
- [ ] PROPOSED: Adapter validation rejects every absent, non-string, sentinel, and lexically invalid profile ID with human-decision-required failure.
- [ ] PROPOSED: New task state receives the exact profile ID.
- [ ] PROPOSED: Every core and agent task operation, including `status` and `next`, rejects missing, malformed, or unequal task project IDs before success output or mutation.
- [ ] PROPOSED: Both schemas express the same approved lexical/type contract, while runtime enforces profile/task equality.
- [ ] PROPOSED: Bootstrap initializes a new target from the exact caller value without changing the donor profile or bypassing immutability for an existing installation.
- [ ] PROPOSED: The current canonical profile and task state remain `nomphi-sdlc` and are not modified by implementation.

## Tests required

### Unit

- [ ] PROPOSED: Table-test the project-ID predicate across every valid/invalid category and non-string type listed under Edge cases.
- [ ] PROPOSED: Verify accepted input is returned/used unchanged and no task-ID helper or normalization is involved.
- [ ] PROPOSED: Assert both schema properties retain string type and carry the exact approved pattern.

### Integration

- [ ] PROPOSED: In isolated copied fixtures, initialize an uninitialized profile with a valid grammar sample and assert exact persistence.
- [ ] PROPOSED: For invalid candidates, assert nonzero exit, no success line, and byte-for-byte unchanged profile content.
- [ ] PROPOSED: Assert equal-ID initialization succeeds without changing identity and different-valid-ID initialization fails without changing any profile byte.
- [ ] PROPOSED: Place each invalid type/category in an isolated profile and verify `doctor` fails; verify task creation fails without creating a task directory.
- [ ] PROPOSED: Create a task, verify exact copy, then tamper its project ID to missing, malformed, and different-valid values; verify `status`, `next`, one mutating core command, and agent `inspect` reject without mutation.
- [ ] PROPOSED: Verify representative normal task operations continue when profile and task IDs are equal and valid.
- [ ] PROPOSED: Verify task-ID traversal rejection and uppercase task-ID behavior remain unchanged.

### E2E

- [ ] PROPOSED: Bootstrap an empty temporary repository with an approved-format caller value, then run doctor, task creation, state read, and agent inspection; assert the exact value persists in profile and task state.
- [ ] PROPOSED: Bootstrap with invalid input and assert nonzero exit, no valid target identity, and unchanged source profile.
- [ ] PROPOSED: Use unrelated target-directory and project-name values and assert neither affects the stored caller-supplied ID.
- [ ] PROPOSED: Run `python3 -m unittest discover -s tests -v` successfully.

## Regression risks

- The current test fixture assumptions (`REPLACE_ME` source and uppercase project IDs) conflict with current identity and the approved format.
- README's uppercase bootstrap example will become invalid.
- Optional example adapter identifiers will fail the tightened lexical contract if loaded as active adapters; assigning replacement identities requires separate human authority.
- `status` and `next` change from adapter-independent reads to fail-closed identity-checked reads.
- Re-running `project-init` with a different value changes from overwrite to rejection.
- Schema consumers may reject historical files accepted by the prior minimum-length rule.
- Bootstrap target staging must never write back to the source profile.

## Dependencies / migrations

- PROPOSED: Add no third-party dependency; use existing Python standard-library `re`/`json`, shell tooling, `unittest`, and subprocess fixture patterns.
- PROPOSED: Perform no automatic normalization or migration of an established project identity.
- PROPOSED: Treat incompatible historical active projects as uninitialized only when their profile ID is already invalid; a human must explicitly supply their valid canonical ID.
- PROPOSED: Leave optional example profile IDs unchanged in this task and document that they are not conforming active-adapter values.
- PROPOSED: Update test fixtures and documentation examples without changing the current canonical profile or task state.

## Unknowns / decisions required

No unresolved material decisions. The requirement supplies the identifier contract, the current profile supplies this project's human-selected valid identity, and the target-only bootstrap staging above resolves the existing donor/target immutability conflict without creating another identity source.

## Definition of Done

- [ ] PROPOSED: Runtime and both schemas implement the approved lexical, immutability, exact-copy, and mismatch-rejection contracts.
- [ ] PROPOSED: Bootstrap establishes only an explicit caller-supplied target identity and leaves the donor profile untouched.
- [ ] PROPOSED: Required unit, integration, and E2E coverage passes via `python3 -m unittest discover -s tests -v`.
- [ ] PROPOSED: Documentation states the accepted format, explicit-human initialization rule, immutability, and compatibility behavior.
- [ ] PROPOSED: Current canonical identity files, optional example identities, workflow state, and unrelated behavior remain unmodified by implementation.
