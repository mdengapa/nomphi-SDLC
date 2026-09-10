# Implementation Report

Task: NOM-TEST-007

## Implemented

- Added a standalone `project_id` predicate using the approved `^[a-z0-9]+(?:-[a-z0-9]+)*$` grammar.
- Made adapter validation fail closed for non-string and malformed profile identifiers.
- Made `project-init` validate before writing and reject replacement of an established valid identifier.
- Made every task-state load validate the adapter and require an exact valid task/profile identifier match.
- Applied the approved identifier pattern to both JSON schemas.
- Changed bootstrap to reset only the copied target profile to the uninitialized template sentinel before explicit initialization.
- Updated fixtures and added predicate, schema, initialization, adapter, task-load, and bootstrap coverage.

## Checks

- PASS: `python3 -m unittest discover -s tests -v`
  - Completed successfully: 24 tests passed.
- PASS: scope-limited `git diff --check` for NOM-TEST-007 implementation files.
- NOT RUN: project adapter test/typecheck/lint/E2E/security commands. `.nomphi/project/commands.json` configures no commands.

## Deviations

- README changes are deferred to the documentation stage, as required by the approved spec.
- A repository-wide `git diff --check` reports trailing whitespace in pre-existing `.opencode/agents/implementer.md`; it is outside this task's authorized scope and was not modified.

## Contract Changes

- Runtime and schemas now enforce the approved lexical project-ID contract.
- Task-state loads now enforce exact equality with the canonical profile identifier.
