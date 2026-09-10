# Documentation Report

Task: NOM-TEST-007

## Updated documentation

- `README.md` now uses a conforming lowercase bootstrap ID example.
- `README.md` documents the verified project-ID grammar, explicit human-supplied initialization, target-only bootstrap staging, and donor isolation.
- `README.md` documents established-ID immutability, exact task-state copying, and rejection of missing, malformed, or unequal task-state identifiers.
- `README.md` clarifies that optional example adapter identifiers are compatibility examples and are not active-project identities.

## Evidence

- Verification accepted the runtime and schema enforcement of `^[a-z0-9]+(?:-[a-z0-9]+)*$`, explicit initialization, immutable established IDs, exact task-state copies, task/profile mismatch rejection, and donor/target bootstrap isolation.
- The verified implementation permits same-ID `project-init` calls for metadata updates and rejects a different established ID.
- No production code, project identity file, task state, or workflow state was modified during documentation.

## Scope

The accepted specification identifies `README.md` as the documentation-stage change. Project-adapter documentation remains unchanged because it contains no verified product-specific identity contract to update.
