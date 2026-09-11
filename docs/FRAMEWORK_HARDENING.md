# NOM-FWK-008 — Framework Hardening

## Objective

Harden the Nomphi SDLC framework before adding new projects, new automation layers or broader agent autonomy.

The phase is based on defects exposed during the `NOM-TEST-007` smoke. The goal is not to improve model prompting. The goal is to move authority from implicit LLM behavior into deterministic framework contracts.

## Baseline

`NOM-TEST-007` is closed and integrated into `main`.

Validated baseline:
- task reached `RELEASED`;
- end-to-end smoke completed;
- 30 tests passing;
- canonical `project_id` contract validated through the workflow;
- OpenCode bindings exercised with frontier models.

Key commits:
- `a1b29f3` — Merge NOM-TEST-007 project identity smoke
- `e3d7cc3` — Configure OpenCode agent model bindings
- `ba9a263` — Complete NOM-TEST-007 project identity smoke

## Defects exposed by the smoke

1. `ready()` can report false positives/negatives because unresolved literals such as `PENDING` or `REPLACE_ME` are detected in explanatory prose rather than only in structured contract fields.
2. Agents do not consistently fail closed when a required handoff is missing. Documenter continued without the expected handoff.
3. Role separation is stated in prompts and manifests but is not sufficiently enforced by executable permissions and guards.
4. Release-gate robustness and workflow transitions need regression coverage after the project-identity changes.
5. Qwen3 Coder 30B was not reliable enough for editing roles in the smoke. The hardening phase must not depend on it for the critical write path.

## Framework invariant

> Nomphi SDLC must not trust agents to voluntarily obey workflow constraints.

The framework must prevent invalid progression even when an agent attempts to continue.

## Workstream 1 — Structured readiness

### Problem

Global textual scanning of reports for placeholders makes prose part of the execution contract. That produces false signals whenever reports explain unresolved states, quote examples or mention placeholder tokens historically.

### Required behavior

- Readiness must be derived only from explicit structured fields or artifact schema state.
- Explanatory text must never independently block or satisfy a gate.
- Tokens such as `PENDING`, `REPLACE_ME`, `TODO`, `TBD` or equivalent are meaningful only when present in contract fields defined as unresolved.
- Legacy artifacts must either be migrated or rejected explicitly; they must not be heuristically guessed as ready.

### Tests

At minimum:
- unresolved structured field blocks readiness;
- resolved structured field passes despite prose containing `PENDING`;
- report quoting `REPLACE_ME` does not block;
- malformed readiness metadata fails closed;
- missing required readiness metadata fails closed.

## Workstream 2 — Mandatory handoffs

### Required behavior

Each stage declares its required incoming handoff contract.

A stage must abort before work begins if a mandatory handoff is:
- missing;
- empty;
- malformed;
- stale for the current workflow iteration;
- associated with another `project_id`;
- associated with another `task_id`;
- produced by the wrong upstream role/stage;
- incompatible with the current state.

No agent may reconstruct a missing authoritative handoff from repository context or previous prose and continue silently.

### Failure semantics

Handoff failure must:
- leave the workflow in the existing valid state;
- emit a deterministic diagnostic;
- identify the missing/invalid contract;
- route ownership to the upstream stage responsible for producing it.

## Workstream 3 — Enforced separation of duties

Role boundaries must be executable policy, not only prompt text.

### Orchestrator
Allowed:
- inspect state;
- validate contracts;
- package context;
- route to roles;
- request/retry stages;
- perform legal state transitions through deterministic helpers.

Forbidden:
- modify production implementation;
- repair tests or application code;
- author a substitute spec on behalf of Planner;
- waive failed gates.

### Planner
Allowed:
- inspect project/repository context;
- write specification and planning artifacts.

Forbidden:
- modify production implementation;
- mark implementation evidence as verified.

### Implementer
Allowed:
- modify production code and implementation tests within approved scope.

Forbidden:
- alter the approved specification to make implementation fit;
- self-approve verification or release.

### Verifier
Allowed:
- inspect code/diff;
- execute verification;
- add verification-specific tests where policy permits;
- issue ACCEPT/REJECT evidence.

Forbidden:
- silently modify the implementation under review;
- convert a defect into a pass by repairing it in the same verification step.

### Documenter
Allowed:
- update durable documentation to reflect already accepted behavior.

Forbidden:
- modify production behavior;
- invent behavior absent from accepted implementation/specification;
- continue without its required handoff/evidence.

### Release Gate
Allowed:
- evaluate deterministic evidence and mandatory verdicts.

Forbidden:
- waive failures;
- infer missing evidence;
- mix artifacts from different project/task identities.

## Workstream 4 — State machine and release gate regression

The state machine must reject all undeclared transitions.

Release eligibility must prove that:
- every mandatory stage for the task/risk class completed;
- every required artifact is current;
- every artifact belongs to the same canonical `project_id` and `task_id`;
- no unresolved mandatory finding remains;
- mandatory tests/checks pass;
- documentation evidence is present when required;
- no stage was bypassed through direct state editing.

Regression cases must include:
- missing handoff;
- stale handoff;
- artifact from another task;
- artifact from another project;
- manipulated state;
- skipped stage;
- release attempted from an illegal state;
- contradictory verdicts;
- old evidence reused after a new implementation iteration.

## Workstream 5 — Baseline consolidation

After hardening:
- all existing tests must remain green;
- new hardening tests must pass;
- an end-to-end smoke equivalent to `NOM-TEST-007` must complete through `RELEASED`;
- the smoke must include deliberate negative-path probes for handoff, role and release violations;
- model bindings should remain unchanged during the phase unless a binding itself prevents execution.

## Model policy during hardening

Current validated OpenCode bindings:
- Orchestrator: GPT-5.6 Terra / medium
- Planner: GPT-5.6 Sol / high
- Implementer: GPT-5.6 Terra / medium
- Verifier: GPT-5.6 Terra / medium
- Documenter: GPT-5.6 Terra / medium

Bindings are intentionally held stable during `NOM-FWK-008` so framework changes can be evaluated without introducing model changes as a second variable.

Qwen3 Coder 30B is not part of the critical editing path for this phase.

## Exit criteria

`NOM-FWK-008` is complete only when all of the following are true:

1. Readiness is based on structured contracts, not prose scanning.
2. Missing or invalid mandatory handoffs fail closed.
3. Role boundaries are enforced technically for critical actions.
4. Illegal state transitions are rejected deterministically.
5. Release cannot occur with stale, cross-project, cross-task or missing evidence.
6. Regression coverage exists for every defect found in `NOM-TEST-007`.
7. Existing baseline tests plus new hardening tests pass.
8. A full positive-path smoke reaches `RELEASED`.
9. Negative-path smoke cases demonstrate that framework guards cannot be bypassed by agent behavior alone.

## Non-goals

This phase does not add:
- new product/project adapters;
- additional agent roles;
- broader autonomous deployment;
- new model experimentation;
- new orchestration features unrelated to the defects above.

Those changes resume only after the framework baseline is hardened.
