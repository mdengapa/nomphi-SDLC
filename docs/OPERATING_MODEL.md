# Operating model

## Intake
A requirement enters the system with a human-readable goal and initial risk classification.

## Planning
Planner creates a bounded technical contract with explicit acceptance criteria, non-goals, invariants, test plan and Definition of Done.

Planning output is authoritative only when its required structured fields are complete. Explanatory prose does not determine readiness.

## Security design
Security creates a threat model for all tasks required by core/project policy.

## Implementation
Implementer writes code and local tests using the approved spec and project adapter.

Implementation must remain inside approved scope. The Implementer cannot redefine the specification to make an implementation acceptable.

## Verification
Verifier independently tests the implementation against the spec and plausible failure modes.

Verifier must not silently repair the production implementation it is evaluating. A functional defect is rejected back to its owning stage.

## Security audit
Security reviews the final attack surface and checks the threat model against the implementation.

## Documentation
Documenter updates durable docs only after the implementation has been accepted functionally and by security.

Documentation is fail-closed: required upstream handoff/evidence must exist and match the current `project_id`, `task_id` and workflow iteration before documentation work begins.

## Release
Deterministic commands and artifact verdicts determine release eligibility.

Release must reject missing, stale, cross-project or cross-task evidence and any illegal stage transition. Agents cannot waive mandatory gates.

## Handoff discipline
Agents communicate through explicit persistent artifacts. A required handoff is part of the execution contract, not an optional convenience.

A mandatory handoff that is missing, malformed, stale, produced by the wrong stage or associated with another task/project must fail closed. The receiving agent must not reconstruct authoritative context from repository inspection or conversation history and continue.

## Role discipline
Role separation is enforced by framework permissions and guards wherever practical, not only by prompts.

- Orchestrator routes, validates and transitions; it does not implement product code.
- Planner specifies; it does not implement.
- Implementer implements; it does not self-approve.
- Verifier falsifies/accepts; it does not silently fix what it verifies.
- Documenter documents accepted behavior; it does not invent or implement behavior.
- Release evaluates evidence; it does not waive failures.

## Cost model
Model cost/performance choices are configuration. They must not alter architecture or weaken role contracts.

Current hardening baseline uses GPT-5.6 Terra for Orchestrator, Implementer, Verifier and Documenter, and GPT-5.6 Sol for Planner. See `docs/OPENCODE.md`.

## Context discipline
Agents should not ingest the entire repository by default. Context is selected from project profile, invariants, relevant skills, task specification, touched modules and direct dependencies.

## Core-change rule
If a lesson is true only for one product, it is not a core change.

The defects exposed by `NOM-TEST-007` are framework-level because they concern readiness, handoff enforcement, role authority and release integrity independently of any product domain. Their remediation is tracked in `NOM-FWK-008`.
